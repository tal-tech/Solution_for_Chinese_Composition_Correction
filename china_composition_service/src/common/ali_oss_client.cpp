#include "ali_oss_client.h"

#include <iostream>
#include <sstream>

#define UNUSED_PARAM(x) (void)x

std::once_flag AliOSSClient::new_flag_;
std::once_flag AliOSSClient::del_flag_;
AliOSSClient *AliOSSClient::instance_{nullptr};

void AliOSSClient::InitInstance(const std::string &access_key_id, 
                                const std::string &access_key_secret, 
                                const std::string &endpoint, 
                                const std::string &buket_name, 
                                const std::string &dir_name) {
    std::call_once(new_flag_, [&]() {
                   instance_ = new AliOSSClient(access_key_id, 
                                                access_key_secret, 
                                                endpoint, 
                                                buket_name, 
                                                dir_name);
                   });
}

void AliOSSClient::ReleaseInstance() {
    std::call_once(del_flag_, [&]() {
                   delete instance_;
                   instance_ = nullptr;
                   });
}

AliOSSClient::AliOSSClient(const std::string &access_key_id, 
                           const std::string &access_key_secret, 
                           const std::string &endpoint, 
                           const std::string &buket_name, 
                           const std::string &dir_name) 
    : access_key_id_{access_key_id}, 
    access_key_secret_{access_key_secret}, 
    endpoint_{endpoint}, 
    buket_name_{buket_name}, 
    dir_name_{dir_name} {
    InitializeSdk();
    InitConf();
}

AliOSSClient::~AliOSSClient() {
    ShutdownSdk();
}

void AliOSSClient::ReinitializeSdk() {
    ShutdownSdk();
    InitializeSdk();
}

void AliOSSClient::InitConf() {
    conf_.maxConnections = 32;  // connection pool size
    conf_.requestTimeoutMs = 30000;  // request timeout
    conf_.connectTimeoutMs = 30000;  // connect timeout
    auto retry_strategy = std::make_shared<ClientRetryStrategy>(300, 5);
    conf_.retryStrategy = retry_strategy;
}

/**
 * @return:  0: success
 *          -1: request_id is empty
 *          -2: upload content fail
 *          -3: get url fail
 */
int AliOSSClient::PutObjectFromMemory(const std::string &request_id, 
                                      const std::string &data, 
                                      std::string &url) {
    url = "";
    if (request_id.empty() || data.empty()) {
        return -1;
    }

    OssClient client(endpoint_, access_key_id_, access_key_secret_, conf_);
    std::shared_ptr<std::iostream> content = std::make_shared<std::stringstream>();
    *content << data;
    std::string object_name{dir_name_};
    object_name += "/" + request_id + ".jpg";  // fixed suffix
    PutObjectRequest request(buket_name_, object_name, content);

    auto outcome = client.PutObject(request);
    if (!outcome.isSuccess()) {
        std::cout << "put object fail" 
            << ", code: " << outcome.error().Code() 
            << ", message: " << outcome.error().Message() 
            << ", request_id: " << outcome.error().RequestId() 
            << std::endl;
        ReinitializeSdk();
        return -2;
    }

    url = GenerateURL(client, object_name);
    return url.empty()?-3:0;
}

void AliOSSClient::ListAllFiles() {
    OssClient client(endpoint_, access_key_id_, access_key_secret_, conf_);
    ListObjectsRequest request(buket_name_);
    auto outcome = client.ListObjects(request);
    if (!outcome.isSuccess()) {
        std::cout << "put object fail" 
            << ", code: " << outcome.error().Code() 
            << ", message: " << outcome.error().Message() 
            << ", request_id: " << outcome.error().RequestId() 
            << std::endl;
        ReinitializeSdk();
    } else {
        for (const auto &object : outcome.result().ObjectSummarys()) {
            std::cout << "object" 
                << ", name: " << object.Key() 
                << ", size: " << object.Size() 
                << ", lastmodify_time: " << object.LastModified() 
                << std::endl;
        }
    }
}

std::string AliOSSClient::GenerateURL(const std::string &object_name) {
    OssClient client(endpoint_, access_key_id_, access_key_secret_, conf_);
    return GenerateURL(client, object_name);
}

std::string AliOSSClient::GenerateURL(OssClient &client, 
                                      const std::string &object_name) {
    // expire time: five years
    std::time_t t_curr = std::time(nullptr) + 3600*24*365*5;
    auto outcome = client.GeneratePresignedUrl(buket_name_, 
                                               object_name, 
                                               t_curr, 
                                               Http::Get);
    std::string res;
    if (outcome.isSuccess()) {
        res = outcome.result().c_str();

    } else {
        std::cout << "generate url fail" 
            << ", code: " << outcome.error().Code() 
            << ", message:" << outcome.error().Message() 
            << ", request_id: " << outcome.error().RequestId() 
            << std::endl;
    }
    return res;
}

bool ClientRetryStrategy::shouldRetry(const AlibabaCloud::OSS::Error &error, 
                                     long attemped_retries) const {
    if (attemped_retries >= max_retries_) {
        return false;
    }

    long response_code = error.Status();

    if ((response_code == 403 && error.Message().find("RequestTimeTooSkewed")) ||
        (response_code > 499 && response_code < 599)) {
        return true;
    } else {
        switch (response_code) {
        // curl error code
        case (ERROR_CURL_BASE + 7):  // CURLE_COULDNT_CONNECT
        case (ERROR_CURL_BASE + 18): // CURLE_PARTIAL_FILE
        case (ERROR_CURL_BASE + 23): // CURLE_WRITE_ERROR
        case (ERROR_CURL_BASE + 28): // CURLE_OPERATION_TIMEDOUT
        case (ERROR_CURL_BASE + 52): // CURLE_GOT_NOTHING
        case (ERROR_CURL_BASE + 55): // CURLE_SEND_ERROR
        case (ERROR_CURL_BASE + 56): // CURLE_RECV_ERROR
            return true;
        default:
            break;
        };
    }

    return false;
}

long ClientRetryStrategy::calcDelayTimeMs(const AlibabaCloud::OSS::Error &error, 
                                          long attemped_retries) const {
    UNUSED_PARAM(error);
    return (1 << attemped_retries) * scale_factor_;
}
