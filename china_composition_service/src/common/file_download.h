#pragma once

#include <string>
#include <vector>


bool Trans2InnerUrl(const std::string &request_id, 
                    std::vector<std::string> &image_urls, 
                    const std::string &trans_url, 
                    std::string &err_msg, 
                    unsigned int timeout_seconds=3);

bool DownloadImage(const std::string &image_url, 
                   std::string &image_data, 
                   double &img_size, 
                   std::string &err_msg, 
                   unsigned int timeout_seconds=1);

