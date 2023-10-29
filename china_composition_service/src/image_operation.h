#pragma once

#include "service_error.h"

#include "opencv2/opencv.hpp"


TALError GetImageData(std::string &image_data, 
                      const std::string &image_url,
                      const std::string &image_base64, 
                      unsigned int download_timeout_seconds=3, 
                      unsigned int retry_count=3, 
                      unsigned int retry_sleep_millsecods=500);

TALError DecodeImage(cv::Mat &dest_img, 
                     const std::string &src_img);

enum class ImageFormat{UNKNOWN, PNG, JPG, JPEG, BMP};
ImageFormat CheckImageFormat(const std::string &image_binary);
bool ImageToBase64(const cv::Mat& src_img, std::string& dst_img, const std::string& format = "jpg", int quality=100);
