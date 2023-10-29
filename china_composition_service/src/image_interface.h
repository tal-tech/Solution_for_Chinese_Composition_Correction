#pragma once

#include "tal_interface.h"

#include <string>
#include <vector>
#include "opencv2/opencv.hpp"


/**
 * 当前图像类的输入一般分为两类：
 * 1.image_url/image_base64：此种方式一般是对外接口
 * 2.只有image_base64的情形，暂定只在服务内部调用时使用，相关函数带有inner
 */
class ImageInterface : public TALInterface {
protected:
    std::string image_url_;
    std::string image_base64_;
    std::vector<cv::Rect> cv_rects_;
    cv::Mat cv_image_;
    bool m_details;
    bool m_precision;
public:
    ImageInterface() = delete;
    ImageInterface(const std::string &interface_url, 
                   const crow::request &request) : 
        TALInterface{interface_url, request} {}
    ImageInterface(const ImageInterface &) = default;
    ImageInterface &operator=(ImageInterface &) = default;
    ImageInterface(ImageInterface &&) = default;
    ImageInterface &operator=(ImageInterface &&) = default;
    virtual ~ImageInterface() {}

private:
    TALError ParseRectangleData(cv::Rect &cv_rect, 
                                Json::Value &rectangle);

protected:
    TALError VerifyImageParam();
    TALError VerifyInnerImageParam();
    TALError VerifyFaceRectangle(bool optional=false);
    TALError VerifyFaceRectangles(bool optional=false);
    void TransSingleURL();

    void SendDataFlow(int64_t request_time,
                      int64_t response_time,
                      const TALError &error,
                      const std::string &response);

protected:
    /**
     * 处理策略定义：可以根据实际的情况通过重载来增加，下面是最通用的情况
     */
    // 1.最通用策略：处理输入是image_url/image_base64的图片，对外接口采用
    virtual TALError handler(Json::Value &result) = 0;
    TALError HandleImage();
    void HandleRequest(std::string &response);

    // 2.处理输入时image_base64的图片，一般作为内部服务时使用
    TALError HandleInnerImage();
    void HandleInnerRequest(std::string &response);
};
