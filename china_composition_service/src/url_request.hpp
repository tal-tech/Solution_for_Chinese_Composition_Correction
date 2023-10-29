/*
 * url_request.hpp
 *
 *  Created on: 2020年5月18日
 *      Author: ym
 */

#ifndef SRC_DET_LIP_URL_REQUEST_HPP_
#define SRC_DET_LIP_URL_REQUEST_HPP_

#include <iostream>
#include <map>
#include <string>
#include <curl/curl.h>

class URLRequest {
private:
	URLRequest();
	~URLRequest();
	URLRequest(const URLRequest &r);
	URLRequest &operator =(const URLRequest &r);
public:
	static URLRequest *instance();
	bool request(std::string url, std::map<std::string, std::string> &header, std::string &body,
			std::string &response, int timeout=1000, int retry = 1);
	bool request(std::string url, std::map<std::string, std::string> &header, const char *body, size_t size,
		std::string &response, int timeout=1000, int retry = 1);
private:
	static size_t OnWriteData(void* buffer, size_t size, size_t nmemb, void* lp_void);
private:
	static URLRequest s_request;
};


#endif /* SRC_DET_LIP_URL_REQUEST_HPP_ */
