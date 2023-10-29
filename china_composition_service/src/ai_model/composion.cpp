/*
 * composion.cpp
 *
 *  Created on: 2021年3月16日
 *      Author: ym
 */

#include <iostream>
#include <vector>
#include <future>
#include <json/json.h>
#include <opencv2/opencv.hpp>
#include "composion.hpp"

#include "base/logging.h"

using namespace std;
using namespace facethink;
using namespace Json;

Composion Composion::s_instance;

Composion *Composion::instance() {
	return &s_instance;
}

bool Composion::_init() {
	std::string dir = "../model/det_chn_comp/";
	m_det = DetChnComp::create(dir + "textsnake_chs.trt", dir + "config.ini");
	if (m_det == nullptr) {
		cout << "init det new error." << endl;
		return false;
	}

	std::string yolov_dir = "../model/det_chn_yolov5/";
	m_yolov5 = DetChnYolo::create(yolov_dir + "yolov5l.engine", yolov_dir + "config.ini");
	if (m_yolov5 == nullptr) {
		cout << "init yolov5 det error." << endl;
		return false;
	}

	std::string rec_dir = "../model/rec_chn_comp/";
	m_rec_old = RecChnComp::create(rec_dir + "rec_chn_rec_v0603.trt", rec_dir + "config.ini", rec_dir + "zidian_new_5883.txt");
	if (m_rec_old == nullptr) {
		cout << "init rec error" << endl;
		return false;
	}

	m_rec_new = RecChnComp::create(rec_dir + "rec_chn_comp_jm_v1.0.0.trt", rec_dir + "config.ini", rec_dir + "zidian_new_5859.txt");
	if (m_rec_new == nullptr) {
		cout << "init rec error" << endl;
		return false;
	}

	m_tps = new std::ThreadPool(1);
	if (m_tps == nullptr) {
		cout << "init tps error" << endl;
		return false;
	}
	return true;
}

bool Composion::init() {
	return Composion::instance()->_init();
}

Composion::Composion() {
	m_tps = nullptr;
	m_rec_new = nullptr;
	m_rec_old = nullptr;
	m_det = nullptr;
	m_yolov5 = nullptr;
}

Composion::~Composion() {
	if (m_tps)
		delete m_tps;
	if (m_rec_new)
		delete m_rec_new;
	if (m_rec_old)
		delete m_rec_old;
	if (m_det)
		delete m_det;

	if (m_yolov5)
		delete m_yolov5;
}

void parse_char_info(Json::Value &infos, Json::Value &input, std::string section) {
	for (auto i = 0; i < input["char_pos"].size(); ++i) {
		Value pos;
		Json::Value result;
		pos["x"] = input["char_pos"][i][0];
		pos["y"] = input["char_pos"][i][1];
		result["char_location"].append(pos);

		for (auto &loc : input["char_box"][i]) {
			Value ploc;
			ploc["x"] = loc[0];
			ploc["y"] = loc[1];
			result["char_location"].append(ploc);
		}

		for (auto &top : input["char_arr"][i]) {
			Json::Value info;
			info["char_ocr_result"] = top[0];
			info["char_confidence"] = top[1];
			result[section].append(info);
		}

		infos.append(result);
	}
}

void parse_title_info(Json::Value &result, Json::Value &input, bool details) {
	if (input.size() == 0) {
		return;
	}

	Json::Value val = input;
	if (!val.isMember("text")) {
		return;
	}

	if (val["text"].isNull())
		return;

	if (val["text"].asString().size() == 0)
		return;
	result["title_ocr_result"] = val["text"];
	if (!details) {
		return;
	}
	parse_char_info(result["title_char_info"], val, "char_ocr_topn");
}

void parse_eassy_info(Json::Value &result, Json::Value &input, bool details) {
	if (input.size() == 0) {
		return;
	}

	for (auto &eaasy : input) {
		Json::Value lines;
		bool flag = false;
		for (auto &line : eaasy) {
			Json::Value info;
			if (line["text"].isNull())
				continue;

			if (line["text"].asString().size() == 0)
				continue;
			flag = true;
			info["line_ocr_result"] = line["text"];
			if (details) {
				parse_char_info(info["line_char_info"], line, "line_char_topn");
			}
			lines.append(info);
		}
		if (flag)
			result["para_ocr_result"].append(lines);
	}
}

bool parse_result(std::string &requestid, std::string &str, Json::Value &result, bool details, bool prcision) {
	if (str.size() == 0) {
		return true;
	}

	try {
		Json::Reader reader;
		Json::Value root;
		std::string title = "title_info";
		std::string essay = "essay_info";

		if (!reader.parse(str, root)) {
			LOG(INFO) << requestid << " reader json parse error.";
			return false;
		}
		if (prcision) {
			title = "title_info_sec";
			essay = "essay_info_sec";
		}

		if (root.isMember("title")) {
			parse_title_info(result[title], root["title"], details);
		}
		if (root.isMember("texts")) {
			parse_eassy_info(result[essay], root["texts"], details);
		}
	} catch(exception &e) {
		LOG(INFO) << requestid << "parse json err " << e.what();
		return false;
	}

	return true;
}

bool Composion::parse_task(bool details, bool prcision, std::string trace_id, cv::Mat &img, Json::Value &result) {
	std::vector<cv::Mat> input_imgs;
	std::vector<std::vector<float>> mgs;
	std::vector<cv::Mat> title_poly;
	std::vector<std::pair<int, cv::Mat>> text_poly;
	std::vector<cv::Mat> img_list;
	std::vector<std::vector<float>> areas;
	future<int> fu;
	int ret;

	std::string new_result;
	std::string old_result;
	input_imgs.emplace_back(img);

	{
		double predict_used=0.0;
	    double post_used =0.0;
		std::lock_guard<std::mutex>  lock(m_det_yolov5_mutex);
		if (m_yolov5->detection(input_imgs, areas, predict_used, post_used) != 0) {
			LOG(INFO) << trace_id << " process yolov5 det err.";
			return false;
		}
	}

	{
		std::lock_guard<std::mutex>  lock(m_det_new_mutex);
		if (m_det->detection(input_imgs, areas, mgs, title_poly, text_poly, img_list) != 0) {
			LOG(INFO) << trace_id << " process det err.";
			return false;
		}
	}

    for (int j = 0; j < img_list.size(); j++) {
        img_list[j].convertTo(img_list[j], CV_8U);
    }

	if (img_list.size() == 0 || text_poly.size() == 0) {
		return true;
	}

	if (prcision) {
		fu = m_tps->commit([&img_list, &mgs, &title_poly, &text_poly, &new_result, this](){
			return this->m_rec_new->detection(img_list, mgs, title_poly, text_poly, new_result);
		});
	}

	{
		LOG(INFO) << "==================================================imgs " << img_list.size() << " title " << title_poly.size() << " texts " << text_poly.size();
		std::lock_guard<std::mutex>  lock(m_rec_old_mutex);
		ret = m_rec_old->detection(img_list, mgs, title_poly, text_poly, old_result);
	}


	//确保成功
	if (prcision) {
		if (fu.get() != 0) {
			LOG(INFO) << trace_id << " new detect parse error.";
			return false;
		}
	}

	if (ret != 0) {
		LOG(INFO) << trace_id << " old detect parse error.";
		return false;
	}

	if (!parse_result(trace_id, old_result, result, details, false)) {
		LOG(INFO) << trace_id << " parse result error";
		return false;
	}

	if (prcision && !parse_result(trace_id, new_result, result, details, true)) {
		LOG(INFO) << trace_id << " parse result error";
		return false;
	}

//	result["jm"] = old_result;
//	if (prcision)
//		result["zt"] = new_result;
	LOG(INFO) << trace_id << " parse detect success";
	return true;
}
