//
// Created by txn on 2/18/19.
//

#include "eureka_client.h"
#include <string>
#include <functional>
//#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <chrono>
#include <sstream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "eureka/json/json.h"
#include "base/logging.h"
#include "crow_all.h"

#define HEART_BEAT_INTERVAL 3

EurekaClient::EurekaClient(std::string eureka_host, int eureka_port, std::string register_url, std::string app_name, std::string server_host, int server_port)
{
    m_res = CURLE_OK;
    m_headers = nullptr;
    m_eureka_host = eureka_host;
    m_eureka_port = eureka_port;
    m_register_url = register_url;
    m_app_name = app_name;
    m_server_port = itos(server_port);
    m_serverHost = server_host;
    m_ipAddr = getHostIp();
    m_instance = setJsonData();
    m_curl_handler_heartbeat = nullptr;
    m_curl_handler_register = nullptr;
    curlInit();
}

EurekaClient::EurekaClient()
{
}

void EurekaClient::run()
{
    m_thread_running = true;
    m_thread = new thread(&EurekaClient::heartBeatTimer, std::ref(*this), HEART_BEAT_INTERVAL);
}

void EurekaClient::stop_register() {
    string stop_url = string(m_register_url) + "apps/" + string(m_app_name) + "/" + readJsonData("instanceId");
    CURL *stop_curl = curl_easy_init();

    curl_easy_setopt(stop_curl, CURLOPT_URL, stop_url.c_str());
    curl_easy_setopt(stop_curl, CURLOPT_CUSTOMREQUEST, "DELETE");
    curl_easy_setopt(stop_curl, CURLOPT_TIMEOUT, 3);
    m_headers = curl_slist_append(m_headers, "Accept-Encoding: gzip");
    curl_easy_setopt(stop_curl, CURLOPT_HTTPHEADER, m_headers);
    unsigned try_times = 0;
    while (try_times < 3) {
        m_res = curl_easy_perform(stop_curl);
        if (m_res == CURLE_OK) {
            long res_code = 0;
            curl_easy_getinfo(stop_curl, 
                              CURLINFO_RESPONSE_CODE, 
                              &res_code);
            if (res_code == 200) {
                LOG(INFO) << "stop_register : success, url:" << stop_url;
                break;
            } else {
                LOG(ERROR) << "stop_register error, response_code: " << res_code;
            }
        } else {
            LOG(ERROR) << stop_url;
            LOG(ERROR) << "stop_register curl_easy_perform() failed:" << curl_easy_strerror(m_res);
        }
        ++try_times;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    curl_easy_cleanup(stop_curl);

}

void EurekaClient::stop(){
    if (!m_thread_running) {
        return;
    }
    m_thread_running = false;
    if(m_thread != nullptr)
    {
        m_thread->join();
    }

    delete this;
}

EurekaClient::~EurekaClient()
{
    if (m_curl_handler_heartbeat != nullptr) {
        curl_easy_cleanup(m_curl_handler_heartbeat);
        m_curl_handler_heartbeat = nullptr;
    }

    if (m_curl_handler_register != nullptr) {
        curl_easy_cleanup(m_curl_handler_register);
        m_curl_handler_register = nullptr;
    }
    curl_global_cleanup();
}

void EurekaClient::curlInit()
{
    curl_global_init(CURL_GLOBAL_ALL);
}


string EurekaClient::getHostIp()
{
    struct sockaddr_in servaddr;
    struct sockaddr_in clientAddr;
    string ip_addr;
    int sockfd;


    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr(m_eureka_host.c_str());
    servaddr.sin_port = htons(int(m_eureka_port));

    connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr));
    socklen_t client_len = sizeof(clientAddr);
    getsockname(sockfd, (struct sockaddr*)&clientAddr, &client_len);
    ip_addr = inet_ntoa(clientAddr.sin_addr);
    if(m_serverHost.empty())
    {
        m_serverHost = ip_addr;
    }
    return ip_addr;
}


string EurekaClient::itos(int64_t i)
{
    stringstream str_s;
    str_s << i;
    return str_s.str();
}

string EurekaClient::getCurrentTime()
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return itos(tv.tv_sec * 1000 + tv.tv_usec /1000);
}


string EurekaClient::setJsonData()
{
    Json::Value instance_port;
    Json::Value instance_datacenter;
    Json::Value instance_lease;
    Json::Value instance_management_port;

    Json::Value instance_val;
    string instanceId;

    char name[256];
    gethostname(name, sizeof(name));
    string hostNmae = name;
    instanceId = string(hostNmae) + ":" + m_app_name + ":" + m_server_port;

    instance_val["instanceId"] = Json::Value(instanceId);
    instance_val["hostName"]= Json::Value(m_serverHost);
    instance_val["app"]= Json::Value(m_app_name);
    instance_val["ipAddr"] = Json::Value(m_ipAddr);

    instance_port["$"] = Json::Value(m_server_port);
    instance_port["@enabled"] = Json::Value("true");
    instance_val["port"] = Json::Value(instance_port);

    instance_port["$"] = Json::Value(443);
    instance_port["@enabled"] = Json::Value("false");
    instance_val["securePort"] = Json::Value(instance_port);

    instance_val["countryId"] = Json::Value(1);

    instance_datacenter["@class"] = Json::Value("com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo");
    instance_datacenter["name"] = Json::Value("MyOwn");
    instance_val["dataCenterInfo"] = Json::Value(instance_datacenter);


    instance_lease["renewalIntervalInSecs"] = Json::Value(HEART_BEAT_INTERVAL);
    instance_lease["durationInSecs"] = Json::Value(10);
    instance_lease["registrationTimestamp"] = Json::Value(0);
    instance_lease["lastRenewalTimestamp"] = Json::Value(0);
    instance_lease["evictionTimestamp"] = Json::Value(0);
    instance_lease["serviceUpTimestamp"] = Json::Value(0);
    instance_val["leaseInfo"] = Json::Value(instance_lease);

    instance_management_port["management.port"] = Json::Value(m_server_port);
    instance_val["metadata"] = Json::Value(instance_management_port);

    instance_val["homePageUrl"] = Json::Value("http://" + string(m_serverHost) + ":" + string(m_server_port) + "/");
    instance_val["statusPageUrl"] = Json::Value("http://" + string(m_serverHost) + ":" + string(m_server_port) + "/info");
    instance_val["healthCheckUrl"] = Json::Value("http://" + string(m_serverHost) + ":" + string(m_server_port) + "/health");
    instance_val["vipAddress"] = Json::Value(m_app_name);
    instance_val["secureVipAddress"] = Json::Value(m_app_name);
    instance_val["isCoordinatingDiscoveryServer"] = Json::Value("false");

    //
    instance_val["status"] = Json::Value("UP");
    instance_val["overriddenstatus"] = Json::Value("UNKNOWN");

    instance_val["lastUpdatedTimestamp"] = Json::Value(getCurrentTime());
    instance_val["lastDirtyTimestamp"] = Json::Value(getCurrentTime());

    Json::Value post_data;
    post_data["instance"] = Json::Value(instance_val);

    Json::FastWriter writer;
    std::string strWrite = writer.write(post_data);

    return strWrite;
}

string EurekaClient::readJsonData(string json_key)
{
    string json_val;
    Json::Value json_root;
    Json::Reader json_reader;
    if (json_reader.parse(m_instance.data(),json_root))
    {
        json_val = json_root["instance"][json_key].asString();
    }

    return json_val;
}


int EurekaClient::sendHeartBeat()
{
    string instanceid_val = readJsonData("instanceId");
    string lastdirty_val = readJsonData("lastDirtyTimestamp");
    string curl = string(m_register_url) + "apps/" + string(m_app_name) + "/" + instanceid_val + "?status=UP&lastDirtyTimestamp=" + lastdirty_val;
    if (m_curl_handler_heartbeat == nullptr)
    {
        LOG(INFO) << "sendHeartBeat:to create CURL connection";
        m_curl_handler_heartbeat = curl_easy_init();
        curl_easy_setopt(m_curl_handler_heartbeat, CURLOPT_URL, curl.c_str());
        curl_easy_setopt(m_curl_handler_heartbeat, CURLOPT_CUSTOMREQUEST, "PUT");
        curl_easy_setopt(m_curl_handler_heartbeat, CURLOPT_TIMEOUT, 3);
    }

    // Perform the request, res will get the return code
    m_res = curl_easy_perform(m_curl_handler_heartbeat);

    // Check for errors
    if (m_res != CURLE_OK)
    {
        LOG(ERROR) << curl;
        LOG(ERROR) << "heart beat curl_easy_perform() failed:" << curl_easy_strerror(m_res);
        CROW_LOG_ERROR << "heart beat curl_easy_perform() failed:" << curl_easy_strerror(m_res);
        return -1;
    }
    long res_code = 0;
    curl_easy_getinfo(m_curl_handler_heartbeat, 
                      CURLINFO_RESPONSE_CODE, 
                      &res_code);
    if (res_code != 200) {
        LOG(ERROR) << "heart beat eureka error, response_code: " << res_code;
        return -2;  // 需要立即重新注册
    }

    //LOG(INFO) << "sendHeartBeat: success";
    return 0;
}


int EurekaClient::registerEureka()
{
    string curl= string(m_register_url) + "apps/" + string(m_app_name);
    if (m_curl_handler_register == nullptr)
    {
        m_curl_handler_register = curl_easy_init();
        curl_easy_setopt(m_curl_handler_register, CURLOPT_URL, curl.c_str());
        m_headers = curl_slist_append(m_headers, "Content-Type: application/json");
        curl_easy_setopt(m_curl_handler_register, CURLOPT_HTTPHEADER, m_headers);

        // set POST JSON data
        curl_easy_setopt(m_curl_handler_register, CURLOPT_POSTFIELDS, m_instance.c_str());
        curl_easy_setopt(m_curl_handler_register, CURLOPT_CUSTOMREQUEST, "POST");
        curl_easy_setopt(m_curl_handler_register, CURLOPT_TIMEOUT, 3);
    }

    // Perform the request, res will get the return code
    m_res = curl_easy_perform(m_curl_handler_register);

    // Check for errors
    if (m_res != CURLE_OK)
    {
        LOG(ERROR) << "register xxxxx 011100  eureka failed:" << curl_easy_strerror(m_res);
        CROW_LOG_ERROR << "register eureka failed:" << curl_easy_strerror(m_res);
        return -1;
    }

    long res_code = 0;
    curl_easy_getinfo(m_curl_handler_register, 
                      CURLINFO_RESPONSE_CODE, 
                      &res_code);
    if (res_code != 204) {
        LOG(ERROR) << "register to eureka error, response_code: " << res_code;
        return -2;
    }

    LOG(INFO) << "register success";
    return 0;
}

void EurekaClient::heartBeatTimer(int time_interval)
{
    int try_count = 0;
    registerEureka();
    const int max_try_count = 6;
    while(m_thread_running)
    {
        std::this_thread::sleep_for(std::chrono::seconds(time_interval));
        if(try_count > max_try_count)
        {
            if(registerEureka() == 0)
            {
                try_count = 0;
            }
        } else {
            int res = sendHeartBeat();
            if (res == -1) {
                try_count++;
            } else if (res == -2) {
                try_count = max_try_count + 1;
            }
        }
    }
    std::this_thread::sleep_for(std::chrono::seconds(1));
    stop_register();
}
