#include "init_server.h"

#include "base/files/file_path.h"
#include "base/files/file_util.h"

#include "base/strings/string_number_conversions.h"
#include "eureka/eureka_client.h"
#include "kafka_client.h"
#include "data_flow.h"
#include "apollo_client.h"
#include "eureka/json/json.h"
#include "conf_param.h"
#include "eureka/eureka_client.h"
#include "distribute_lock.h"
#include "redis_conn_pool.h"
#include "mysql_conn_pool.h"
#include "ali_oss_client.h"
#include "apollo_conf.h"
#include "tal_interface.h"
#include "composion.hpp"


using namespace facethink;
CURRENT_ENV g_current_env{CURRENT_ENV::LOCAL};

void GetCurrentEnv() {
    char *current_env;
    while (!(current_env=getenv("CURRENT_ENV"))) {
        sleep(1);
        LOG(ERROR) << "retry to get CURRENT_ENV";
    }

    if (strcmp(current_env, "LOCAL") == 0) {
        g_current_env = CURRENT_ENV::LOCAL;
    } else if (strcmp(current_env, "TEST") == 0) {
        g_current_env = CURRENT_ENV::TEST;
    } else if (strcmp(current_env, "PRE") == 0) {
        g_current_env = CURRENT_ENV::PRE;
    } else if (strcmp(current_env, "PROD") == 0) {
        g_current_env = CURRENT_ENV::PROD;
    } else {
        LOG(ERROR) << "unknown env: " << current_env;
        exit(-1);
    }
    LOG(INFO) << "current env: " << static_cast<int>(g_current_env);
}

void GetHostName(std::string &host_name) {
    char hname[200] = { 0 };
    int index;
    while (gethostname(hname, sizeof(hname)) != 0) {
        sleep(1);
        LOG(ERROR) << "retry get hostname";
    }
    host_name = hname;
    index = host_name.rfind("-");
    assert(index > 0);
    host_name = host_name.substr(0, index);
    index = host_name.rfind("-");
    assert(index > 0);
    host_name = host_name.substr(0, index);
}

static EurekaClient *g_eureka_client{nullptr};
void ConnectEureka() {
    if (g_current_env == CURRENT_ENV::LOCAL) {
        return;
    }
    int service_port = ConfParam::GetValue(APOLLO_LOCAL_SERVICE_PORT, 
                                           6732);
    std::string eureka_host{ConfParam::GetValue(APOLLO_PAAS_EUREKA_HOST, "")};
    int eureka_port = ConfParam::GetValue(APOLLO_PAAS_EUREKA_PORT, 0);
    std::string eureka_register_url{ConfParam::GetValue(APOLLO_PAAS_EUREKA_URL, 
                                                        "")};
    std::string app_name{ConfParam::GetValue(APOLLO_PAAS_EUREKA_APP_NAME, 
                                             "")};

    std::string server_host;
    GetHostName(server_host);
    g_eureka_client = new EurekaClient(eureka_host, 
                                    eureka_port, 
                                    eureka_register_url, 
                                    app_name, 
                                    server_host, 
                                    service_port);
    g_eureka_client->run();
}

void ReleaseEureka() {
    if (g_current_env == CURRENT_ENV::LOCAL) {
        return;
    }
    g_eureka_client->stop();
}

bool DumpCallback(const google_breakpad::MinidumpDescriptor &descr, 
                  void *context, 
                  bool succeeded) {
    ReleaseEureka();
    return succeeded;
}

// 初始化日志，将日志写入文件，example：
// [16486:16486:2018/10/12/16-47-32:INFO:Godeye.cpp(79)] log message
void InitLog() {
    LoggingSettings settings;
    // 日志输出目的地(默认控制台)
    // LOG_TO_SYSTEM_DEBUG_LOG(DEBUG控制台),LOG_TO_ALL(文件和控制台)
    LoggingDestination destination = LOG_TO_SYSTEM_DEBUG_LOG;
    settings.logging_dest = destination;

    InitLogging(settings);
    // 参数1：进程ID，参数2：线程ID，参数3：时间戳，参数4：TickCount，
    // 默认只显示时间戳
    SetLogItems(true, true, true, false);
    SetMinLogLevel(LOG_INFO);
}

bool ReadConfigFile() {
    std::string config_file{"config/config.ini"};
    File file(FilePath(config_file), 
              base::File::FLAG_OPEN_ALWAYS | base::File::FLAG_READ);
    if(file.error_details() != File::FILE_OK) {
        LOG(FATAL) << "open config file error:" 
            << file.ErrorToString(file.error_details());
        return false;
    }

    int64_t file_size = file.GetLength();
    char *file_buf = new char[file_size + 1];
    memset(file_buf, 0, file_size + 1);

    file.ReadAtCurrentPos(file_buf, file_size + 1);
    if (ConfParam::ParseParam(file_buf) != 0) {
        LOG(FATAL) << "parse config file error";
        delete []file_buf;
        return false;
    }

    delete []file_buf;
    return true;
}

void InitKafka() {
    std::string mq_host{ConfParam::GetValue(APOLLO_COMMON_DF_HOST, "")};
    std::string topic{ConfParam::GetValue(APOLLO_COMMON_DF_TOPIC, "")};
    KafkaClient::GetInstance()->Init(mq_host, topic);
    std::string api_type{ConfParam::GetValue(APOLLO_LOCAL_API_TYPE, "")};
    DataFlow::SetApiType(api_type);
    std::string biz_type = ConfParam::GetValue(CONF_SERVICE_TYPE, 
                                           "other");
    DataFlow::SetBizType(biz_type);
}

// TODO：由于pod重启后所有文件丢失，所以生成dump文件意义不大，修改调整：
// 将输出dump信息到文件改为输出到标准输出
void InitDumpFile() {
    // breakpad 只接受绝对路径的dump dir
    FilePath dump_dir{ConfParam::GetValue(APOLLO_LOCAL_DUMP_DIR, "./")};
    if (!dump_dir.IsAbsolute()) {
        dump_dir = base::CommandLine::ForCurrentProcess()->
            GetProgram().DirName().Append(dump_dir);
    }

    File::Error* error{nullptr};
    if (!CreateDirectoryAndGetError(dump_dir, error)) {
        LOG(FATAL) << "failed to create dump dir:" 
            << dump_dir.AsUTF8Unsafe()
            << " error:" << File::ErrorToString(*error);
        return;
    }

    google_breakpad::MinidumpDescriptor descriptor(dump_dir.AsUTF8Unsafe());
    // minidump文件目录
    google_breakpad::ExceptionHandler eh(descriptor, 
                                         nullptr, 
                                         DumpCallback, 
                                         nullptr, 
                                         true, 
                                         -1);
}

void ConnectApollo() {
    std::string apollo_host{ConfParam::GetValue(CONF_APOLLO_HOST, 
                                                "")};
    std::string apollo_app_id{ConfParam::GetValue(CONF_APOLLO_APPLICATION, 
                                                  "")};
    if (apollo_host.empty() || apollo_app_id.empty()) {
        LOG(ERROR) << "apollo host or app id is null";
        exit(-1);
    }
    LOG(INFO) << "apollo_host: " << apollo_host
              << ", apollo_app_id: " << apollo_app_id;

    auto callback = [](const std::string &name_space, 
                       const base::DictionaryValue *data_dict) {
        if (name_space == "datawork-common") {
            std::string kafka_host;
            data_dict->GetString("kafka-bootstrap-servers", 
                                 &kafka_host);
            ConfParam::SetValue(APOLLO_COMMON_DF_HOST, 
                                kafka_host);

            std::string type = ConfParam::GetValue(CONF_SERVICE_TYPE, 
                                                   "other");
            std::string topic;
            data_dict->GetString(type, &topic);
            ConfParam::SetValue(APOLLO_COMMON_DF_TOPIC, topic);

            // 需要动态变化的配置,更新响应模块
            KafkaClient::GetInstance()->Topic() = topic;
            LOG(INFO) << "datawork-common config change from apollo: " 
                << "kafka_host = " << kafka_host 
                << ", kafka_topic = " << topic;
        } else if (name_space == "application") {
            std::string apollo_config;
            auto update_conf = [&data_dict, &apollo_config]
                (const std::string &key) ->bool {
                    std::string new_value;
                    data_dict->GetString(key, &new_value);
                    std::string old_value = ConfParam::GetValue(key, "");
                    ConfParam::SetValue(key, new_value);
                    apollo_config += key + "=" + new_value + ",";
                    return old_value==new_value;
            };

            for (auto const &key : APOLLO_BASE_CONF_ITEM) {
                update_conf(key);
            }
            for (auto const &key : APOLLO_OSS_CONF_ITEM) {
                update_conf(key);
            }
            for (auto const &key : APOLLO_MYSQL_CONF_ITEM) {
                update_conf(key);
            }
            for (auto const &key : APOLLO_REDIS_CONF_ITEM) {
                update_conf(key);
            }
            for (auto const &key : APOLLO_DIST_LOCK_CONF_ITEM) {
                update_conf(key);
            }

            LOG(INFO) << "config from apollo: " << apollo_config;
        }
    };

    static ApolloClient client(apollo_app_id, "default", apollo_host);
    client.Start(callback);
}

static void ReadEnvConfig() {
    char *env_conf = nullptr;
    for (const auto &item : ENV_CONF_ITERM) {
        while (!(env_conf=getenv(item.c_str()))) {
            sleep(1);
            LOG(ERROR) << "retry to get env: " << item;
        }
        ConfParam::SetValue(item, std::string{env_conf});
    }
}

static bool init_ali_oss = false;
static void InitAliOSS() {
    std::string key_id{ConfParam::GetValue(APOLLO_OSS_ACCESS_KEY_ID, "")};
    std::string secret{ConfParam::GetValue(APOLLO_OSS_ACCESS_KEY_SECRET, "")};
    std::string endpoint{ConfParam::GetValue(APOLLO_OSS_ENDPOINT, "")};
    std::string bucket_name{ConfParam::GetValue(APOLLO_OSS_BUKETNAME, "")};
    std::string dir_name{ConfParam::GetValue(APOLLO_OSS_DIR, "")};
    if (endpoint.empty()) {
        return;
    }
    AliOSSClient::InitInstance(key_id, secret, endpoint, bucket_name, dir_name);
    init_ali_oss = true;
    LOG(INFO) << "init ali_oss";
}

static void ReleaseAliOSS() {
    if (!init_ali_oss) {
        return;
    }
    AliOSSClient::ReleaseInstance();
}

static void InitMySQLConn(unsigned pool_size=0) {
    std::string host{ConfParam::GetValue(APOLLO_MYSQL_HOST, "")};
    std::string user{ConfParam::GetValue(APOLLO_MYSQL_USER, "")};
    std::string password{ConfParam::GetValue(APOLLO_MYSQL_PW, "")};
    std::string db_name{ConfParam::GetValue(APOLLO_MYSQL_DBNAME, "")};
    if (host.empty()) {
        return;
    }
    auto size = pool_size;
    if (pool_size == 0) {
        size = ConfParam::GetValue(APOLLO_MYSQL_POOLSIZE, 16);
    }
    sql_utils::mysql::MySQLConnPool::InitInstance(host,
                                                  user,
                                                  password,
                                                  db_name,
                                                  size);
    LOG(INFO) << "init mysql conn pool";
}

static bool init_redis = false;
static void InitRedisConn(unsigned pool_size=0) {
    std::string host{ConfParam::GetValue(APOLLO_REDIS_HOST, "")};
    if (host.empty()) {
        return;
    }
    auto port = ConfParam::GetValue(APOLLO_REDIS_PORT, 6379);
    std::string password{ConfParam::GetValue(APOLLO_REDIS_PW, "")};
    auto db_num = ConfParam::GetValue(APOLLO_REDIS_DB, 0);
    auto size = pool_size;
    if (pool_size == 0) {
        size = ConfParam::GetValue(APOLLO_REDIS_POOLSIZE, 64);
    }
    redis_utils::RedisConnPool::InitInstance(host,
                                             port,
                                             password,
                                             db_num,
                                             size);
    init_redis = true;
    LOG(INFO) << "init redis";
}

static void ReleaseRedisConn() {
    if (!init_redis) {
        return;
    }
    redis_utils::RedisConnPool::ReleaseInstance();
}

bool init_dist_lock = false;
static void InitDistributeLock() {
    int retry_count = ConfParam::GetValue(APOLLO_DIST_LOCK_RETRY_COUNT, -1);
    int interval = ConfParam::GetValue(APOLLO_DIST_LOCK_INTERVAL, -1);
    if (retry_count==-1 || interval==-1) {
        return;
    }
    DistributeLock::InitInstance(retry_count, interval);
    init_dist_lock = true;
}

void ReleaseDistributeLock() {
    if (!init_dist_lock) {
        return;
    }
    DistributeLock::ReleaseInstance();
}

void InitService() {
    InitLog();
    LOG(INFO) << "init service";

    GetCurrentEnv();  // 获取服务当前运行环境
    if (g_current_env == CURRENT_ENV::LOCAL) {
        ReadConfigFile(); // 读取本地配置文件：只有LOCAL环境才会读取
    } else {
        ReadEnvConfig();
    }

    ConnectApollo();  // 连接apollo，获取apollo配置

    InitDumpFile();   // 初始化dump文件，NOTE：需要将其打印到标准输出
    InitKafka();      // 初始化Kafka连接等信息-数据回流

    // 这些配置项需要在apollo中进行配置后才会初始化
    // InitAliOSS();     // 初始化阿里云OSS
    // InitMySQLConn();  // 初始化MySQL连接池
    // InitRedisConn();  // 初始化Redis连接池
    // InitDistributeLock();  // 初始化分布式锁

    LOG(INFO) << "basic initialization is done";
    if (!Composion::init()) {
    	LOG(INFO) << "composion init error.";
    	exit(-1);
    }
    LOG(INFO) << " init composion ok";
}

void ReleaseService() {
    ReleaseEureka();  // 需要首先取消注册中心的注册

    ReleaseAliOSS();
    ReleaseRedisConn();
    ReleaseDistributeLock();

}

void Listen(RequestEvents &events) {
    std::string app_name{ConfParam::GetValue(APOLLO_PAAS_EUREKA_APP_NAME, 
                                             "UNDEFINED")};
    TALInterface::SetAppName(app_name);

    crow::SimpleApp app;
    for (auto &event : events) {
        auto func = [&](const crow::request &request) {
            std::string response;
            event.second(request, response);
            return crow::response{response};
        };
        auto &url = event.first.first;
        if (event.first.second == HTTP_METHOD::POST) {
            app.route_dynamic(url.c_str()).methods("POST"_method)(func);
        } else if (event.first.second == HTTP_METHOD::PUT) {
            app.route_dynamic(url.c_str()).methods("PUT"_method)(func);
        } else if (event.first.second == HTTP_METHOD::GET){
            app.route_dynamic(url.c_str()).methods("GET"_method)(func);
        } else if (event.first.second == HTTP_METHOD::UPDATE) {
            app.route_dynamic(url.c_str()).methods("UPDATE"_method)(func);
        } else {
            LOG(ERROR) << "unsupport http method: " 
                << (int)event.first.second;
        }
    }
    ConnectEureka();
    int service_port = ConfParam::GetValue(APOLLO_LOCAL_SERVICE_PORT, 
                                           6732);
    app.port(service_port).multithreaded().run();
}
