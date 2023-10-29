#include "data_flow.h"

std::string DataFlow::api_type_{"0"};
std::string DataFlow::biz_type_{"datawork-image"};

DataFlow::DataFlow() {
    m_root_[data_api_type] = api_type_;
    m_root_[data_biz_type] = biz_type_;
}

DataFlow::~DataFlow() {
}

void DataFlow::SetSourceInfos(bool b_url, 
                              const std::string &value, 
                              const std::string &request_id) {
    if (value.empty()) {
        m_root_[data_source_infos] = Json::arrayValue;
        return;
    }

    Json::Value source_info;
    source_info[data_source_id] = request_id;
    source_info[data_source_content] = value;
    if (b_url) {
        source_info[data_source_type] = "url";
    } else {
        source_info[data_source_type] = "base64";
    }
    m_root_[data_source_infos].append(source_info);
}

void DataFlow::TransDataToJson(const std::string &type, 
                               const std::string &data) {
    Json::Value json_root;
    Json::Reader json_reader;
    if (json_reader.parse(data.data(), json_root)) {
        if (type == trans_body_json) {
            if (json_root.isObject() && 
                json_root.isMember("image_base64") && 
                json_root["image_base64"].isString() && 
                !((json_root["image_base64"].asString()).empty())) {
                Json::FastWriter writer;
                Json::Value del_data;
                json_root.removeMember("image_base64", &del_data);
                std::string str_source = writer.write(json_root);
                Json::Value json_param;
                json_param["requestParam"] = str_source;
                m_root_[data_source_remark] = json_param;
            } else {
                Json::Value json_param;
                json_param["requestParam"] = data;
                m_root_[data_source_remark] = json_param;
            }
        } else if (type == trans_response_json) {
            m_root_[data_ret_data] = json_root;
        }
    } else {
        Json::Value json_param;
        json_param["requestParam"] = data;
        m_root_[data_source_remark] = json_param;
    }
}

std::string DataFlow::GetJsonData() {
    Json::FastWriter writer;
    return std::move(writer.write(m_root_));
}
