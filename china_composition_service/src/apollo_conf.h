#pragma once

#include <string>

// 配置文件/环境变量关于apollo的配置项
const std::string CONF_APOLLO_HOST{"APOLLO_HOST"};
const std::string CONF_APOLLO_APPLICATION{"APOLLO_APPLICATION"};
// 业务类型：image speech text other
const std::string CONF_SERVICE_TYPE{"SERVICE_TYPE"};

const std::string ENV_CONF_ITERM[] = {
    CONF_APOLLO_HOST, 
    CONF_APOLLO_APPLICATION, 
    CONF_SERVICE_TYPE
};


// apollo中的数据回流配置项：datawork-common
const std::string APOLLO_COMMON_DF_HOST{"common.df_host"};
const std::string APOLLO_COMMON_DF_TOPIC{"common.df_topic"};


// apollo中的基础配置项: application
const std::string APOLLO_LOCAL_DUMP_DIR{"local_dump_dir"};
const std::string APOLLO_LOCAL_SERVICE_PORT{"local_service_port"};
// 接口类型：0-同步；1-异步
const std::string APOLLO_LOCAL_API_TYPE{"local_api_type"};
const std::string APOLLO_PAAS_EUREKA_HOST{"paas_eureka_host"};
const std::string APOLLO_PAAS_EUREKA_PORT{"paas_eureka_port"};
const std::string APOLLO_PAAS_EUREKA_URL{"paas_eureka_url"};
const std::string APOLLO_PAAS_EUREKA_APP_NAME{"paas_eureka_app_name"};
const std::string APOLLO_DATAFLOW_URL_TRANS_HOST{"dataflow_url_trans_host"};
const std::string APOLLO_DATAFLOW_URL_TRANS_TIMEOUT{"dataflow_url_trans_timeout"};
const std::string APOLLO_DATAFLOW_URL_TRANS_RETRY{"dataflow_url_trans_retry"};
const std::string APOLLO_AUTOMATIC_URL{"paas_automatic_aurl"};


const std::string APOLLO_BASE_CONF_ITEM[] = {
    APOLLO_LOCAL_DUMP_DIR, 
    APOLLO_LOCAL_SERVICE_PORT, 
    APOLLO_LOCAL_API_TYPE, 
    APOLLO_PAAS_EUREKA_HOST, 
    APOLLO_PAAS_EUREKA_PORT, 
    APOLLO_PAAS_EUREKA_URL, 
    APOLLO_PAAS_EUREKA_APP_NAME, 
    APOLLO_DATAFLOW_URL_TRANS_HOST, 
    APOLLO_DATAFLOW_URL_TRANS_TIMEOUT, 
    APOLLO_DATAFLOW_URL_TRANS_RETRY,
    APOLLO_AUTOMATIC_URL
};


// 阿里云OSS配置项-若apollo未配置则不会初始化
const std::string APOLLO_OSS_ACCESS_KEY_ID{"oss_access_key_id"};
const std::string APOLLO_OSS_ACCESS_KEY_SECRET{"oss_access_key_secret"};
const std::string APOLLO_OSS_ENDPOINT{"oss_endpoint"};
const std::string APOLLO_OSS_BUKETNAME{"oss_bucket_name"};
const std::string APOLLO_OSS_DIR{"oss_dir"};

const std::string APOLLO_OSS_CONF_ITEM[] = {
    APOLLO_OSS_ACCESS_KEY_ID, 
    APOLLO_OSS_ACCESS_KEY_SECRET, 
    APOLLO_OSS_ENDPOINT, 
    APOLLO_OSS_BUKETNAME, 
    APOLLO_OSS_DIR
};


// Redis配置项-若apollo未配置则不会初始化
const std::string APOLLO_REDIS_HOST{"redis_host"};
const std::string APOLLO_REDIS_PORT{"redis_port"};
const std::string APOLLO_REDIS_PW{"redis_password"};
const std::string APOLLO_REDIS_DB{"redis_db"};
const std::string APOLLO_REDIS_POOLSIZE{"redis_pool_size"};

const std::string APOLLO_REDIS_CONF_ITEM[] = {
    APOLLO_REDIS_HOST, 
    APOLLO_REDIS_PORT, 
    APOLLO_REDIS_PW, 
    APOLLO_REDIS_DB, 
    APOLLO_REDIS_POOLSIZE
};


// MySQL配置项-若apollo未配置则不会初始化
const std::string APOLLO_MYSQL_HOST{"mysql_host"};
const std::string APOLLO_MYSQL_USER{"mysql_user"};
const std::string APOLLO_MYSQL_PW{"mysql_password"};
const std::string APOLLO_MYSQL_DBNAME{"mysql_dbname"};
const std::string APOLLO_MYSQL_POOLSIZE{"mysql_pool_size"};

const std::string APOLLO_MYSQL_CONF_ITEM[] = {
    APOLLO_MYSQL_HOST, 
    APOLLO_MYSQL_USER, 
    APOLLO_MYSQL_PW, 
    APOLLO_MYSQL_DBNAME, 
    APOLLO_MYSQL_POOLSIZE
};


// 基于Redis分布式锁配置项-若apollo未配置则不会初始化
const std::string APOLLO_DIST_LOCK_RETRY_COUNT{"dist_lock_retry_count"};
const std::string APOLLO_DIST_LOCK_INTERVAL{"dist_lock_interval"};

const std::string APOLLO_DIST_LOCK_CONF_ITEM[] = {
    APOLLO_DIST_LOCK_RETRY_COUNT, 
    APOLLO_DIST_LOCK_INTERVAL
};


// 下面增加其他配置项
