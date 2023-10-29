//
// Created by txn on 2/18/19.
//

#ifndef APOLLO_CLIENT_H
#define APOLLO_CLIENT_H


#include <curl/curl.h>
#include <string>
#include <thread>
#include <map>
#include "base/values.h"

using namespace std;

class ApolloClient
{
    typedef std::map<std::string, int> NotyMap;
    typedef void Callback(const std::string &, const base::DictionaryValue *);
public:
    ApolloClient();
    ApolloClient(const std::string &app_id, const std::string &cluster = "default", const std::string &config_server_url =
        "http://localhost:8080", int time_out = 35, const std::string &ip = "");

    ~ApolloClient();

    void Start(Callback *callback);

    void Stop();

    void Listener();

private:
    void InitIP(std::string ip);

    void LongPoll();

    void UNCachedHTTPGet(std::string name_space = "application");

    string _app_id;
    string _cluster;
    int _timeout;
    volatile bool _stopped;
    string _config_server_url;
    string _ip;
    volatile bool _stopping;
    NotyMap _notification_map;
    std::thread *thd_listener;
    Callback *_callback;
};


#endif //APOLLO_CLIENT_H
