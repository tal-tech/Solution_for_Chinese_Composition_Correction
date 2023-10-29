#pragma once

#include "eureka/json/json.h"
#include "kafka_client.h"

const std::string data_api_id = "apiId";
const std::string data_api_name = "apiName";
const std::string data_api_type = "apiType";
const std::string data_biz_type = "bizType";
const std::string data_appkey = "appKey";
const std::string data_version = "version";
const std::string data_url = "url";
const std::string data_request_id = "requestId";
const std::string data_request_time = "requestTime";
const std::string data_response_time = "responseTime";
const std::string data_code = "code";
const std::string data_msg = "msg";
const std::string data_err_code = "errCode";
const std::string data_err_msg = "errMsg";
const std::string data_duration = "duration";
const std::string data_send_time = "sendTime";
const std::string data_source_infos = "sourceInfos";
const std::string data_source_id = "id";
const std::string data_source_type = "sourceType";
const std::string data_source_content = "content";
const std::string data_source_remark = "sourceRemark";
const std::string data_ret_data = "data";
const std::string data_remark = "dataRemark";
const std::string data_tag = "tag";
const std::string trans_body_json = "body";
const std::string trans_response_json = "response";

class DataFlow {
public:
    DataFlow();
    ~DataFlow();

public:
    template<typename V>
    void SetValue(const std::string &key, const V &value);
    // 目前只支持：图像url、base64，暂不支持其他类型
    void SetSourceInfos(bool b_url, 
                        const std::string &value, 
                        const std::string &request_id);

    void TransDataToJson(const std::string &type, 
                         const std::string &data);
    std::string GetJsonData();

private:
    Json::Value m_root_;

    // 接口类型：0-同步；1-异步
    static std::string api_type_;
    /**
     * 业务类型/接口分类：
     * 
     */
    static std::string biz_type_;

public:
    static void SetApiType(const std::string &api_type) {
        api_type_ = api_type;
    }

    static void SetBizType(const std::string &biz_type) {
        if (biz_type.compare("image") == 0) {
            biz_type_ = "datawork-image";
        } else if (biz_type.compare("speech") == 0) {
            biz_type_ = "datawork-speech";
        } else if (biz_type.compare("text") == 0) {
            biz_type_ = "datawork-text";
        } else if (biz_type.compare("other") == 0) {
            biz_type_ = "datawork-other";
        }
    }
};

template<typename V> inline 
void DataFlow::SetValue(const std::string &key, 
                        const V &value) {
    m_root_[key] = value;
}
