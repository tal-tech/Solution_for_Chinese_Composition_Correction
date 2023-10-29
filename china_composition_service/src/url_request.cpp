/*
 * url_request.cpp
 *
 *  Created on: 2020年5月18日
 *      Author: ym
 */

#include "url_request.hpp"
#include "base/logging.h"

using namespace std;
using namespace logging;

URLRequest URLRequest::s_request;

URLRequest::URLRequest() {
	curl_global_init(CURL_GLOBAL_DEFAULT);
}

URLRequest::~URLRequest() {
	curl_global_cleanup();
}

URLRequest *URLRequest::instance() {
	return &s_request;
}

size_t URLRequest::OnWriteData(void* buffer, size_t size, size_t nmemb, void* lp_void) {
    std::string* str = dynamic_cast<std::string*>((std::string *)lp_void);
    if (nullptr == str || nullptr == buffer) {
        return -1;
    }
    char* p_data = (char*)buffer;
    str->append(p_data, size * nmemb);
    return nmemb;
}

bool URLRequest::request(string url, map<string, string> &header, string &body, string &response,
		int timeout, int retry) {
    return request(url, header, body.c_str(), body.size(), response, timeout, retry);
}

bool URLRequest::request(string url, map<string, string> &header, const char *body, size_t size, string &response,
		int timeout, int retry) {
	CURL *curl = curl_easy_init();
	long res_code = -1;
	response = "";
	struct curl_slist *li = nullptr;
	li = curl_slist_append(li, "Content-Type: application/json");
	for (auto it = header.begin(); it != header.end(); ++it) {
		li = curl_slist_append(li, (it->first + ": " + it->second).c_str());
	}
	for (int i = 0; i < retry; ++i) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);
//        curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);
        if (size != 0) {
			curl_easy_setopt(curl, CURLOPT_POST, 1);
			curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body);
        } else {
//        	curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "GET");
        }
        curl_easy_setopt(curl, CURLOPT_READFUNCTION, NULL);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&response);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, URLRequest::OnWriteData);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, li);
        curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1);
        curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT_MS, timeout);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, timeout);
        int ret = curl_easy_perform(curl);

        if(ret == CURLE_OK) curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &res_code);
        if (res_code == 200) {
        	break;
        }

        LOG(INFO) << url << " request error code : " << res_code;
	}
	curl_slist_free_all(li);
	curl_easy_cleanup(curl);
	if (res_code != 200)
		return false;
	return true;
}
