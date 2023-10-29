///////////////////////////////////////////////////////////////////////////////////////
///  Copyright (C) 2017, TAL AILab Corporation, all rights reserved.
///
///  @file: rec_chn_comp.hpp
///  @brief 中文作文识别模块
///  @details 最初版本
//
//
///  @version 1.0.0.0
///  @author Jie He
///  @date 2021-03-12
///
///  @see 使用参考：performance_testing.cpp
///
///////////////////////////////////////////////////////////////////////////////////////
#ifndef __FACETHINK_API_REC_CHN_COMP_HPP__
#define __FACETHINK_API_REC_CHN_COMP_HPP__
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
	class EXPORT_CLASS RecChnComp {
	public:
		EXPORT_CLASS_API explicit RecChnComp(void);
		EXPORT_CLASS_API virtual ~RecChnComp(void);
		
		/// \brief SDK初始化函数，必须先于任何其他SDK函数之前调用，create的重载函数。
		/// @param [in] det_model_file 指定SDK对应的模型文件路径。
		/// @param [in] config_file 指定SDK对应的参数配置文件路径,详情见config.ini文件。
		/// @param [in] dict_file 指定SDK对应的字典文件路径。
		/// @return
		/// @remarks 初始化函数需要读取模型等文件，需要一定时间等待。
		EXPORT_CLASS_API static RecChnComp* create(
			const std::string& det_model_file,
			const std::string& config_file,
			const std::string& dict_file);

	

		/// \brief 中文作文文本识别。
		/// @param [in] img 输入的图像数据，仅支持灰度图，一般为检测模块输出结果:
		/// @param [in] input_imgs检测结果图片组成的矩阵
		/// @param [in] is_rgb_format，默认值为false时，表示图片格式为BGR。
		/// @param [in] mgs，模型输出的margin组成的向量
		/// @param [in] title_poly，模型输出的标题多边形矩阵组成的向量
		/// @param [in] text_poly，模型输出的作文内容多边形矩阵组成的向量
		/// @param [out] jsontxt，模型输出的识别结果组成的json字符串
		/// @return
		/// @retval 0 检测成功。
		/// @retval -1 图片为空或图片通道不为3或输入人体框为空
		/// @retval -2 模型运行出错。
		/// @retval -5 SDK本地鉴权失败
		/// @retval -6 数据上传模块参数配置错误
		EXPORT_CLASS_API virtual int detection(std::vector<cv::Mat>& input_imgs,
											std::vector<std::vector<float>> mgs, 
											std::vector<cv::Mat> title_poly, 
											std::vector<std::pair<int, cv::Mat>> text_poly,
											std::string& jsontxt,
											bool is_rgb_format = false) = 0;


	};
}
#endif