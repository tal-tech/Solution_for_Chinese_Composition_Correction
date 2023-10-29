/*
 * composion.hpp
 *
 *  Created on: 2021年3月16日
 *      Author: ym
 */

#ifndef IMAGE_SRC_AI_MODEL_COMPOSION_HPP_
#define IMAGE_SRC_AI_MODEL_COMPOSION_HPP_

#include <iostream>
#include <mutex>

#include <iostream>
#include <string>
#include "opencv2/opencv.hpp"
#include <json/json.h>
#include "det_chn_comp.hpp"
#include "rec_chn_comp.hpp"
#include "det_chn_yolov5.hpp"
#include "threadpool.hpp"

class Composion {
public:
	static Composion *instance();
	static bool init();
public:
	bool parse_task(bool details, bool prcision, std::string id, cv::Mat &img, Json::Value &result);
private:
	Composion();
	~Composion();
private:
	bool _init();
private:
	std::mutex m_det_new_mutex;
	std::mutex m_det_yolov5_mutex;
	std::mutex m_rec_old_mutex;
	std::mutex m_rec_new_mutex;
	facethink::DetChnComp *m_det;
	facethink::DetChnYolo *m_yolov5;
	facethink::RecChnComp *m_rec_old;
	facethink::RecChnComp *m_rec_new;
	std::ThreadPool *m_tps;
private:
	static Composion s_instance;
};



#endif /* IMAGE_SRC_AI_MODEL_COMPOSION_HPP_ */
