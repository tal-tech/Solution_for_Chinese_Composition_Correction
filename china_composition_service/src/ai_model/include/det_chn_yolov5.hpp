///////////////////////////////////////////////////////////////////////////////////////
///  Copyright (C) 2017, TAL AILab Corporation, all rights reserved.
///
///  @file: cls_paper_blank.hpp
///  @brief 检测试卷空白
///  @details 最初版本
//
//
///  @version 1.0.0.0
///  @author Yu Qiao
///  @date 2020-02-05
///
///  @see 使用参考：demo.cpp
///
///////////////////////////////////////////////////////////////////////////////////////
#ifndef __FACETHINK_API_DET_CHN_YOLOV5_HPP__
#define __FACETHINK_API_DET_CHN_YOLOV5_HPP__
#include <string>
#include <math.h>
#include <opencv2/opencv.hpp>
#ifdef WIN32
#ifdef DLL_EXPORTS
#define EXPORT_CLASS   __declspec(dllexport)
#define EXPORT_API  extern "C" __declspec(dllexport)
#define EXPORT_CLASS_API
#else
#define EXPORT_CLASS   __declspec(dllimport )
#define EXPORT_API  extern "C" __declspec(dllimport )
#endif
#else
#define EXPORT_CLASS
#define EXPORT_API  extern "C" __attribute__((visibility("default")))
#define EXPORT_CLASS_API __attribute__((visibility("default")))
#endif
namespace facethink {
	class EXPORT_CLASS DetChnYolo {
	public:
		EXPORT_CLASS_API explicit DetChnYolo(void);
		EXPORT_CLASS_API virtual ~DetChnYolo(void);
		
		/// \brief SDK初始化函数，必须先于任何其他SDK函数之前调用，create的重载函数。
		/// @param [in] det_model_file 指定SDK对应的模型文件路径。
		/// @param [in] config_file 指定SDK对应的参数配置文件路径,详情见config.ini文件。
		/// @return
		/// @remarks 初始化函数需要读取模型等文件，需要一定时间等待。
		EXPORT_CLASS_API static DetChnYolo* create(
			const std::string& det_model_file,
			const std::string& config_file);

	

		/// \brief 主区域检测。
		/// @param [in] img 输入的图像数据，支持如下两种种种格式:
		/// - 1.BGR图：img为一维数组，每个元素（字节）表示一个像素点的单通道取值，三个连续元素表示一个像素点的三通道取值，顺序为BGR。
		/// - 2.RGB图：此时is_rgb_format应设置为true。
		/// @param [in] input_imgs,待检测的图像，虽然是vector，但只支持单图像的输入
		/// @param[out]final_boxes,接收主区域检测框，两层vector，最外层的是框维度，一张图可以有多个主区域，内层是矩形框维度，一个矩形框由x1,y1,x2,y2组成.(x1,y1)表示举行框左上角点，(x2,y2)表示右下角点
		/// @param[in] predict_used,接收模型推理耗时
		///@param[in]predict_used,接收后处理耗时
		/// @param [in] is_rgb_format，默认值为false时，表示图片格式为BGR。
		/// @return
		/// @retval 0 检测成功。
		/// @retval -1 检测失败
		EXPORT_CLASS_API virtual int detection(std::vector<cv::Mat>& input_imgs,                                                       
                                  std::vector<std::vector<float>>& final_boxes, 
								  double &predict_used, 
								  double &post_used,                                 
                                  bool is_rgb_format=false) = 0;
	};
}
#endif
