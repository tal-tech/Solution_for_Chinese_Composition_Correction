#include "file_download.h"
#include "base/base64.h"
#include "base/at_exit.h"
#include "base/base_paths.h"
#include "base/command_line.h"
#include "base/files/file_path.h"
#include "base/files/file_util.h"
#include "base/json/json_reader.h"
#include "base/json/json_writer.h"
#include "base/location.h"
#include "base/logging.h"
#include "base/path_service.h"
#include "base/time/time.h"
#include "base/values.h"
#include "breakpad/src/client/linux/handler/exception_handler.h"
#include "json/json.h"
#include "curl/curl.h"

#include <iostream>
#include <stdlib.h>
#include <unistd.h>
#include <atomic>


using namespace base;

static size_t OnWriteData(void *buffer, 
                          size_t size, 
                          size_t nmemb, 
                          void *lp_void) {
    std::string *str = dynamic_cast<std::string*>((std::string*)lp_void);
    if (nullptr == str || nullptr == buffer) {
        return 0;
    }
    str->append((char*)buffer, size * nmemb);
    return size * nmemb;
}

bool Trans2InnerUrl(const std::string &request_id, 
                    std::vector<std::string> &image_urls, 
                    const std::string &trans_url, 
                    std::string &err_msg, 
                    unsigned int timeout_seconds) {
    Json::Value root;
    for (const auto &image_url : image_urls) {
        root["urls"].append(image_url);
    }
    root["requestId"] = request_id;
    root["sendTime"] = base::Time::Now().ToJavaTime();
    Json::FastWriter writer;
    std::string trans_body = writer.write(root);

    CURL *curl = curl_easy_init();
    if (!curl) {
        err_msg = "failed to init curl";
        return false;
    }

    std::string trans_response;
    curl_easy_setopt(curl, CURLOPT_URL, trans_url.c_str());
    curl_easy_setopt(curl, CURLOPT_POST, 1);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, trans_body.c_str());
    curl_easy_setopt(curl, CURLOPT_READFUNCTION, NULL);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, OnWriteData);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&trans_response);
    struct curl_slist *li = nullptr;
    li = curl_slist_append(li, "content-type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, li);
    curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1);
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 1);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout_seconds);
    CURLcode ret = curl_easy_perform(curl);

    long res_code = 0;
    if(ret == CURLE_OK) {
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &res_code);
    }
    if (li) {
        curl_slist_free_all(li);
    }
    curl_easy_cleanup(curl);

    if (ret == CURLE_COULDNT_CONNECT) {
        err_msg = "connection disconnect";
        return false;
    } else if (ret == CURLE_OPERATION_TIMEDOUT) {
        err_msg = "request timeout";
        return false;
    } else if (ret!=CURLE_OK || trans_response.empty()) {
        err_msg = "trans url error: code: " + std::to_string(ret);
        err_msg += std::string{", msg: "} + curl_easy_strerror(ret);
        return false;
    }

    if(res_code != 200) {
        err_msg = "error on http code: " + std::to_string(res_code);
        return false;
    }

    scoped_ptr<base::Value> value = base::JSONReader::Read(trans_response);
    if (!value) {
        err_msg = "failed to parse result: " + trans_response;
        return false;
    }

    base::DictionaryValue *root_dict = nullptr;
    if (!value->GetAsDictionary(&root_dict)) {
        err_msg = "cannot cast response as dictionary: " + trans_response;
        return false;
    }

    int ret_code = 0;
    if (!root_dict->GetInteger("code", &ret_code)) {
        err_msg = "cannot find code in response: " + trans_response;
        return false;
    }
    if (ret_code != 2000000) {
        std::string error_msg;
        root_dict->GetString("msg", &error_msg);
        err_msg = "error code: " + std::to_string(ret_code);
        err_msg += ", error msg: " + error_msg;
        err_msg += ", image url: ";
        for (auto &image_url : image_urls) {
            err_msg += image_url + "; ";
        }
        return false;
    }

    base::ListValue *data_list = nullptr;
    if (!root_dict->GetList("resultBean", &data_list)) {
        err_msg = "cannot get resultBean in response: " + trans_response;
        return false;
    }

    std::vector<std::string> inner_urls;
    for (auto list_node : *data_list) {
        base::DictionaryValue* dict_valude = nullptr;
        if (list_node->GetAsDictionary(&dict_valude)) {
            std::string temp;
            dict_valude->GetString("innerUrl", &temp);
            inner_urls.push_back(temp);
        } else {
            err_msg = "cannot get resultBean's value: " + trans_response;
        }
    }

    if (inner_urls.size() != image_urls.size()) {
        err_msg = "inner url is empty" + trans_response;
        return false;
    }
    image_urls = std::move(inner_urls);

    return true;
}

static size_t WriteImageData(void *buffer, 
                             size_t size, 
                             size_t nmemb, 
                             void *stream) {
    std::string *tmp = (std::string*)stream;
    if (!tmp) {
        LOG (ERROR) << "failed to be write.";
        return 0;
    }
    tmp->append((char*)buffer, size * nmemb);
    return size * nmemb;
}

bool DownloadImage(const std::string &image_url, 
                   std::string &image_data, 
                   double &img_size, 
                   std::string &err_msg, 
                   unsigned int timeout_seconds) {
    CURL *curl = curl_easy_init();
    if (!curl) {
        err_msg = "failed to curl init";
        return false;
    }

    curl_easy_setopt(curl, CURLOPT_URL, image_url.c_str ());
    curl_easy_setopt(curl, CURLOPT_HEADER, 0);
    curl_easy_setopt(curl, CURLOPT_VERBOSE, 0);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout_seconds);
    curl_easy_setopt(curl, CURLOPT_DNS_CACHE_TIMEOUT, 60 * 60 * 72);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, &WriteImageData);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &image_data);
    CURLcode ret_code = curl_easy_perform (curl);
    curl_easy_getinfo(curl, CURLINFO_CONTENT_LENGTH_DOWNLOAD, &img_size);
    bool res = true;
    if (ret_code != CURLE_OK) {
        res = false;
        err_msg = "download image error, code: " + std::to_string(ret_code);
        err_msg += std::string{", msg: "} + curl_easy_strerror(ret_code);
        err_msg += ", image_url: " + image_url;
    } else {
        long http_code = 0;
        curl_easy_getinfo(curl, 
                          CURLINFO_RESPONSE_CODE, 
                          &http_code);
        if (http_code != 200) {
            err_msg = "download image error, code: " + std::to_string(http_code);
            res = false;
        }
    }
    curl_easy_cleanup(curl);

    return res;
}
