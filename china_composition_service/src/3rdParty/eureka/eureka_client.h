//
// Created by txn on 2/18/19.
//

#ifndef EUREKA_EUREKA_CLIENT_H
#define EUREKA_EUREKA_CLIENT_H


#include <curl/curl.h>
#include <string>
#include <thread>

using namespace std;

class EurekaClient
{
public:
    EurekaClient();
    EurekaClient(std::string eureka_host, int eureka_port, std::string register_url, std::string app_name, std::string server_host, int server_port);

    void heartBeatTimer(int time_interval);
    int registerEureka();
    int sendHeartBeat();
    void run();
    void stop();
    void stop_register();

private:
    void curlInit();
    ~EurekaClient();
    string getHostIp();
    string itos(int64_t i);
    string getCurrentTime();
    string setJsonData();

    string readJsonData(string json_key);

    thread* m_thread;
    string m_instance;
    string m_serverHost;
    string m_eureka_host;
    int m_eureka_port;
    string m_register_url;
    string m_app_name;
    string m_server_port;
    string m_ipAddr;
    curl_slist* m_headers;
    CURLcode m_res;
    CURL* m_curl_handler_register;
    CURL* m_curl_handler_heartbeat;
    volatile bool m_thread_running;
};


#endif //EUREKA_EUREKA_CLIENT_H
