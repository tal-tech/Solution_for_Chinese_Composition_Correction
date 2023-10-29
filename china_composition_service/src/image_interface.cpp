#include "image_interface.h"
#include "data_flow.h"
#include "base/base64.h"
#include "base/logging.h"
#include "base/time/time.h"
#include "file_download.h"
#include "conf_param.h"
#include "apollo_conf.h"
#include "image_operation.h"


TALError ImageInterface::VerifyImageParam() {
	m_details = false;
	m_precision = false;

    if (request_body_json_.isMember("image_base64")) {
        auto &image = request_body_json_["image_base64"];
        if (!image.isString()) {
            return SERVICE_ERROR.E_UNKNOWN_REQ;
        }
        image_base64_ = image.asString();
    }

    if (image_base64_.empty() && 
        request_body_json_.isMember("image_url")) {
        auto &image = request_body_json_["image_url"];
        if (!image.isString()) {
            return SERVICE_ERROR.E_UNKNOWN_REQ;
        }
        image_url_ = image.asString();
    }

    if (image_base64_.empty() && image_url_.empty()) {
    	return SERVICE_ERROR.E_IMAGE_BOTH_NULL;
    }


    if (request_body_json_.isMember("details")) {
    	if (request_body_json_["details"].isBool()) {
    		m_details = request_body_json_["details"].asBool();
		} else {
			return SERVICE_ERROR.E_UNKNOWN_REQ;
		}
    }


    if (request_body_json_.isMember("precision")) {
    	if (request_body_json_["precision"].isBool()) {
    		m_precision = request_body_json_["precision"].asBool();
		}
    }

    return SERVICE_ERROR.E_OK;
}

void ImageInterface::TransSingleURL() {
    std::string error_msg;
    auto trans_url = ConfParam::GetValue(APOLLO_DATAFLOW_URL_TRANS_HOST, "");
    auto timeout = ConfParam::GetValue(APOLLO_DATAFLOW_URL_TRANS_TIMEOUT, 1);
    auto retry = ConfParam::GetValue(APOLLO_DATAFLOW_URL_TRANS_RETRY, 1);
    std::vector<std::string> image_urls{image_url_};
    bool res = false;
    for (int i=0; i<retry; ++i) {
        res = Trans2InnerUrl(request_id_, image_urls, trans_url,
                             error_msg, timeout);
        if (res) {
            break;
        }
    }
    if (!res) {
        LOG(ERROR) << GenerateAlarmMsg(TECHNICAL_ERROR.E_URL_TRANS,
                                       interface_url_,
                                       error_msg);
    } else {
        if (image_urls.size() >= 1) {
            image_url_ = image_urls[0];
        }
    }
}

TALError ImageInterface::HandleImage() {
    TALError res;
    if (((res=ParseRequestBody())!=SERVICE_ERROR.E_OK) || 
        ((res=VerifyImageParam())!=SERVICE_ERROR.E_OK)) {
        return res;
    }
    
    if (image_base64_.empty()) {
        TransSingleURL();
    }

    std::string image_binary;
    res = GetImageData(image_binary, image_url_, image_base64_);
    if (res != SERVICE_ERROR.E_OK) {
        return res;
    }

    res = DecodeImage(cv_image_, image_binary);
    if (res != SERVICE_ERROR.E_OK) {
        return res;
    }

    return res;
}

void ImageInterface::HandleRequest(std::string &response) {
    int64_t request_time = base::Time::Now().ToJavaTime();
    LOG(INFO) << "start, " << request_.raw_url;

    TALError error{SERVICE_ERROR.E_OK};
    Json::Value result;
    do {
        if ((error = HandleImage()) != SERVICE_ERROR.E_OK) {
            break;
        }
        error = handler(result);
    } while (false);

    int64_t response_time = base::Time::Now().ToJavaTime();
    double cost = response_time - request_time;

    Json::Value root;
    root["code"] = Json::Value(error.code);
    root["msg"] = Json::Value(error.message);
    auto duration = 0.0f;
    Json::Value data;
    if (error == SERVICE_ERROR.E_OK) {
        duration = cost;
        data = result;
    }
//    data["process_duration"] = duration;
    root["data"] = data;
    Json::FastWriter writer;
    response = writer.write(root);

    SendDataFlow(request_time, response_time, error, response);
    LOG(INFO) << "end, " << request_.raw_url
        << ", " << error << ", duration:" << cost << "ms";
    MallocTrim();
}

void ImageInterface::SendDataFlow(int64_t request_time,
                                int64_t response_time,
                                const TALError &error,
                                const std::string &response) {
    DataFlow mq_data;
    mq_data.SetValue(data_request_id, request_id_);
    if (!image_base64_.empty()) {
        mq_data.SetSourceInfos(false, image_base64_, request_id_);
    } else if (!image_url_.empty()) {
        mq_data.SetSourceInfos(true, image_url_, request_id_);
    } else {
        mq_data.SetSourceInfos(false, "", request_id_);
    }
    mq_data.SetValue(data_api_name, app_name_);
    mq_data.SetValue(data_url, interface_url_);
    mq_data.SetValue(data_appkey, app_key_);
    std::string api_id = GetURLParamValue(data_api_id);
    mq_data.SetValue(data_api_id, api_id);
    // mq_data.SetValue(data_version, app_host_);
    mq_data.SetValue(data_request_time, request_time);
    mq_data.SetValue(data_response_time, response_time);
    mq_data.SetValue(data_duration, response_time-request_time);
    int64_t res_tm = base::Time::Now().ToJavaTime();
    mq_data.SetValue(data_send_time, res_tm);
    mq_data.SetValue(data_code, error.code);
    mq_data.SetValue(data_err_code, error.code);
    mq_data.SetValue(data_msg, error.message);
    mq_data.SetValue(data_err_msg, error.message);
    mq_data.TransDataToJson(trans_response_json, response);
    mq_data.TransDataToJson(trans_body_json, request_body_);
    std::string mq_message = mq_data.GetJsonData();
    // LOG(INFO) << "data_flow: " << mq_message;
    KafkaClient::GetInstance()->SendMsg(mq_message);
}
