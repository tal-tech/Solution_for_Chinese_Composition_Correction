//
// Created by txn on 2/18/19.
//

#include "apollo_client.h"
#include <string>
#include <functional>
#include <algorithm>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "base/values.h"
#include "base/logging.h"
#include "base/json/json_reader.h"
#include "base/json/json_writer.h"

#include "conf_param.h"
#include "kafka_client.h"

ApolloClient::ApolloClient(const std::string &app_id, const std::string &cluster,
    const std::string &config_server_url, int time_out, const std::string &ip)
{
    InitIP(ip);
    _config_server_url = config_server_url;
    _app_id = app_id;
    _cluster = cluster;
    _timeout = time_out;
    _stopped = false;
    thd_listener = nullptr;
    _stopping = false;
    _notification_map["datawork-common"] = -1;
    _notification_map["application"] = -1;
}

ApolloClient::ApolloClient()
{
}

ApolloClient::~ApolloClient()
{

}

void ApolloClient::InitIP(std::string ip) {
    if(!ip.empty()){
        _ip = ip;
    }else{
        struct sockaddr_in servaddr;
        struct sockaddr_in clientAddr;
        int sockfd;


        sockfd = socket(AF_INET, SOCK_DGRAM, 0);
        memset(&servaddr, 0, sizeof(servaddr));
        servaddr.sin_family = AF_INET;
        servaddr.sin_addr.s_addr = inet_addr("8.8.8.8");
        servaddr.sin_port = htons(53);

        if(connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0){
            LOG(ERROR) << "failed to connect ip 8.8.8.8 while getting ip from apollo";
            return;
        }
        socklen_t client_len = sizeof(clientAddr);
        if(getsockname(sockfd, (struct sockaddr*)&clientAddr, &client_len) < 0){
            LOG(ERROR) << "failed to get sockname from apollo";
            return;
        }
        _ip = inet_ntoa(clientAddr.sin_addr);
    }
}

void ApolloClient::Start(Callback *callback) {
    _callback = callback;
    LongPoll();
    thd_listener = new std::thread(&ApolloClient::Listener, this);
}

void ApolloClient::Stop() {
    _stopping = true;

    if(thd_listener){
        thd_listener->join();

        delete thd_listener;
        thd_listener = nullptr;
    }
}

static size_t OnWriteData(void* buffer, size_t size, size_t nmemb, void* lp_void) {
    std::string* str = dynamic_cast<std::string*>((std::string *)lp_void);
    if (nullptr == str || nullptr == buffer) {
        return -1;
    }
    char* p_data = (char*)buffer;
    str->append(p_data, size * nmemb);
    return nmemb;
}

void ApolloClient::UNCachedHTTPGet(string name_space) {

    CURLcode ret;
    std::string str_response;
    CURL* curl = curl_easy_init();
    if (nullptr == curl){
        LOG(ERROR) << "LongPoll curl_easy_init failed!";
        return;
    }

    std::string url = _config_server_url + "/configs/" + _app_id + "/" + _cluster + "/" + name_space + "/?ip=" + _ip;

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_READFUNCTION, NULL);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, OnWriteData);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&str_response);
    /**
    * 当多个线程都使用超时处理的时候，同时主线程中有sleep或是wait等操作。
    * 如果不设置这个选项，libcurl将会发信号打断这个wait从而导致程序退出。
    */
    curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1);
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, _timeout);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, _timeout);
    ret = curl_easy_perform(curl);

    long res_code = 0;
    if(ret == CURLE_OK) curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &res_code);

    curl_easy_cleanup(curl);

    if(ret != CURLE_OK){
        LOG(ERROR) << "UNCachedHTTPGet curl error: " << curl_easy_strerror(ret);
        return;
    }

    if(res_code != 200){
        LOG(ERROR) << "UNCachedHTTPGet curl error on http code:" << res_code;
        return;
    }

    scoped_ptr<base::Value> value = base::JSONReader::Read(str_response);
    if(!value){
        LOG(ERROR) << "UNCachedHTTPGet failed to parse result json: " + str_response;
        return;
    }

    base::DictionaryValue *root_dict = nullptr;
    if (!value->GetAsDictionary(&root_dict)) {
        LOG(ERROR) << "UNCachedHTTPGet cannot cast root response as DictionaryValue: " << str_response;
        return;
    }

    base::DictionaryValue *data_dict = nullptr;
    if (root_dict->GetDictionary("configurations", &data_dict)) {
        if (_callback != NULL){
            _callback(name_space, data_dict);
        }
    }
    else{
        LOG(ERROR) << "UNCachedHTTPGet response cannot find configurations key: " << str_response;
    }
}

void ApolloClient::LongPoll() {

    //获取body
    base::ListValue list_value;
    for(auto itr : _notification_map){
        base::DictionaryValue dict_value;
        dict_value.SetString("namespaceName", itr.first);
        dict_value.SetInteger("notificationId", itr.second);

        list_value.Append(dict_value.CreateDeepCopy());
    }

    std::string str_post;
    base::JSONWriter::Write(list_value,&str_post);
    char *s_escape = curl_escape(str_post.c_str() , str_post.size());//特殊字符转义

    std::string url = _config_server_url + "/notifications/v2";
    url += "?appId=" + _app_id;
    url += "&cluster=" + _cluster;
    url += "&notifications=" + std::string(s_escape);
    curl_free(s_escape);

    CURLcode ret;
    std::string str_response;
    CURL* curl = curl_easy_init();
    if (nullptr == curl){
        LOG(ERROR) << "LongPoll curl_easy_init failed!";
        return;
    }

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_READFUNCTION, NULL);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, OnWriteData);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&str_response);
    /**
    * 当多个线程都使用超时处理的时候，同时主线程中有sleep或是wait等操作。
    * 如果不设置这个选项，libcurl将会发信号打断这个wait从而导致程序退出。
    */
    curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1);
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, _timeout);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, _timeout);
    ret = curl_easy_perform(curl);

    long res_code = 0;
    if(ret == CURLE_OK) curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &res_code);

    curl_easy_cleanup(curl);

    if(ret != CURLE_OK){
        //LOG(ERROR) << "LongPoll curl error: " << curl_easy_strerror(ret);
        return;
    }

    if(res_code != 200){
        LOG(ERROR) << "LongPoll curl error on http code:" << res_code;
        return;
    }

    scoped_ptr<base::Value> value = base::JSONReader::Read(str_response);
    if(!value){
        LOG(ERROR) << "LongPoll failed to parse result json: " << str_response;
        return;
    }

    base::ListValue *root_list = nullptr;
    if (!value->GetAsList(&root_list)) {
        LOG(ERROR) << "LongPoll cannot cast root response as ListValue: " << str_response;
        return;
    }

    for(auto list_node : *root_list){
        base::DictionaryValue* dict_valude = nullptr;
        if(list_node->GetAsDictionary(&dict_valude)){

            int notification_id = -1;
            std::string namespace_name;

            dict_valude->GetString("namespaceName", &namespace_name);
            dict_valude->GetInteger("notificationId", &notification_id);

            UNCachedHTTPGet(namespace_name);
            _notification_map[namespace_name] = notification_id;
        }else{
            LOG(ERROR) << "LongPoll cannot get root_list's value: " << str_response;
        }
    }
}

void ApolloClient::Listener() {
    while(!_stopping){
        LongPoll();
    }
    _stopped = true;
}
