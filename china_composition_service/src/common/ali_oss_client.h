#ifndef AI_BASED_ABILITY_ALI_OSS_CLIENT_H
#define AI_BASED_ABILITY_ALI_OSS_CLIENT_H

#include "alibabacloud/oss/OssClient.h"
#include "alibabacloud/oss/client/RetryStrategy.h"

#include <string>
#include <mutex>

using namespace AlibabaCloud::OSS;

class AliOSSClient {
public:
    static void InitInstance(const std::string &access_key_id, 
                             const std::string &access_key_secret, 
                             const std::string &endpoint, 
                             const std::string &buket_name, 
                             const std::string &dir_name);
    static void ReleaseInstance();
    static inline AliOSSClient &GetInstance();

    int PutObjectFromMemory(const std::string &request_id, 
                            const std::string &data, 
                            std::string &url);
    int PutObjectFromFile(const std::string &request_id, 
                          const std::string &file_name, 
                          std::string &url);

    void ListAllFiles();  // purpose: for test now

    std::string GenerateURL(const std::string &object_name);

private:
    AliOSSClient(const std::string &access_key_id, 
                 const std::string &access_key_secret, 
                 const std::string &endpoint, 
                 const std::string &buket_name, 
                 const std::string &dir_name);
    ~AliOSSClient();
    
    AliOSSClient(const AliOSSClient &) = delete;
    AliOSSClient &operator=(const AliOSSClient &) = delete;

    void ReinitializeSdk();
    void InitConf();

    std::string GenerateURL(OssClient &client, 
                            const std::string &object_name);

private:
    static std::once_flag new_flag_;
    static std::once_flag del_flag_;
    static AliOSSClient *instance_;

    std::string access_key_id_;
    std::string access_key_secret_;
    std::string endpoint_;
    std::string buket_name_;
    std::string dir_name_;

    ClientConfiguration conf_;
};

// used for retry strategy
class ClientRetryStrategy : public RetryStrategy {
public:
    ClientRetryStrategy(long scale_factor=300, long max_retries=3) 
        : scale_factor_{scale_factor}, max_retries_{max_retries} {
    }

    bool shouldRetry(const AlibabaCloud::OSS::Error &error, 
                     long attemped_retries) const;
    long calcDelayTimeMs(const AlibabaCloud::OSS::Error &error, 
                         long attemped_retries) const;

private:
    long scale_factor_;  // scale factor for retrywaiting time
    long max_retries_;
};

AliOSSClient &AliOSSClient::GetInstance() {
    return *instance_;
}

#endif  // AI_BASED_ABILITY_ALI_OSS_CLIENT_H
