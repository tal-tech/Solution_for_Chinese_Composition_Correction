#include "rec_chn_comp.hpp"
#include <iostream>
#include <fstream>
#include <chrono>
#include <string>
#include <iomanip>

#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/sinks/text_file_backend.hpp>
#include <boost/log/utility/setup/file.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/sources/record_ostream.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/ini_parser.hpp>
#include <boost/filesystem.hpp>
#include <boost/io/ios_state.hpp>
#include <boost/progress.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <boost/algorithm/string/split.hpp>
#include <boost/lexical_cast.hpp>
#include <opencv2/opencv.hpp>

using namespace facethink;
using namespace std;
using namespace cv;

void setupLog(std::string filename) {
    typedef boost::log::sinks::synchronous_sink< boost::log::sinks::text_file_backend > sink_t;
    boost::property_tree::ptree pt;
    boost::shared_ptr< sink_t > file_sink = boost::log::add_file_log
            (
                    boost::log::keywords::auto_flush = true,
                    boost::log::keywords::file_name = filename,
                    boost::log::keywords::format = "[%TimeStamp%]: %Message%"
            );
    boost::log::add_common_attributes();
    int log_level = pt.get<int>("log_level", 2);
    boost::log::core::get()->set_filter(boost::log::trivial::severity >= log_level);
}

std::vector<std::string>getFilePath(std::string folder_path) {
    namespace fs = boost::filesystem;
    fs::directory_iterator end;
    int file_count = 0;
    std::vector<std::string>filePaths;
    for (fs::directory_iterator dir(folder_path); dir != end; dir++)
    {
        std::string fn = dir->path().string();
        //std::cout << fn << std::endl;
        filePaths.push_back(fn);
    }
    return filePaths;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0]
                  << " det_model"
                  << " image folder"
                  << " config file" << std::endl;
        return 1;
    }

    setupLog("rec_chn_comp_performance.log");
    const std::string det1_model = argv[1];
    const std::string images_folder = argv[2];
    const std::string config_file = argv[3];
    const std::string dict_file = argv[4];
    const int max_batch = argc > 5 ? std::stoi(argv[5]) : 1;
    int repeat_count = argc > 5 ? std::stoi(argv[6]) : 1;
    // int output_to_file = argc > 5 ? std::stoi(argv[7]) : 1;

    std::cout << "running ... ,please wait" << std::endl;

    std::ifstream ifs(dict_file);  //读取文件
	if(!ifs.good()) {
        std::cerr << "read zidian failed" << std::endl;
		BOOST_LOG_TRIVIAL(error) << "read zidian failed:" << dict_file;
		return -1;
	}
	// std::string line;
	// std::vector<std::string> lines;
	// while(std::getline(ifs, line)) {
    //     // std::cout << line.find("\n") << std::endl;
    //     if (line.find("\r") != std::string::npos) {
    //         line = line.replace(line.find("\r"), 1, "");
    //     }
	// 	lines.push_back(line);   //将每一行依次存入到vector中
	// }
	// ifs.close();

    RecChnComp *text_detector = RecChnComp::create(
            det1_model,
            config_file,
            dict_file);
    std::cout << "load over" << std::endl;
    double cost_time_all = 0.0;
    int count = 0;

    std::vector<double> vecCost;
    //int max_batch = 2;
    for (int i = 0; repeat_count <= 0 || i < repeat_count; i++) {
        std::vector<std::string> imgs_path = getFilePath(images_folder);
        int start_index = 0;
	vecCost.clear();
        int img_size = imgs_path.size();
        while (start_index < img_size) {
            int count1 = std::min(max_batch, img_size - start_index);
            std::vector<cv::Mat> input_imgs;
            std::string img_path_concat = "";
            for (int i = 0; i < count1; i++) {
                std::string img_path = imgs_path[start_index + i];
                // std::string img_path = "/home/hejie/Documents/AILab/AIEngine/rec_chn_comp/release/rec_chn_comp_700.100.1.0.1.2/images/testing/" + std::to_string(i+1) + ".png";
                std::cout << img_path << std::endl;
                img_path_concat += img_path + " ";
                cv::Mat img = cv::imread(img_path, 0);
                // cv::cvtColor(img, img, cv::COLOR_BGR2GRAY);
                if (img.data == 0 || img.cols <= 0 || img.rows <=0) {
                    BOOST_LOG_TRIVIAL(error) << "read image failed:" << img_path;
                    continue;
                }
                input_imgs.push_back(img);
            }
            start_index += count1;
            if (input_imgs.size() != count1) continue;
            std::cout << "start_index: " << start_index << std::endl;
            std::vector<std::vector<float>> probs;
            auto time_start = std::chrono::steady_clock::now();
            std::vector<std::vector<float>> mgs;
            std::vector<cv::Mat> title_poly;
            std::vector<std::pair<int, cv::Mat>> text_poly;
            std::string jsontxt = "";
            std::cout << "reading img: " << img_path_concat << std::endl;
	    for(int i = 0; i < input_imgs.size();i++)
	    {
	        text_poly.emplace_back(0,cv::Mat());
	    }
            int ret = text_detector->detection(input_imgs, mgs, title_poly, text_poly, jsontxt, false);
            BOOST_LOG_TRIVIAL(info) << img_path_concat << " result:";
            BOOST_LOG_TRIVIAL(info) << jsontxt;
            if (ret < 0) {
                BOOST_LOG_TRIVIAL(info) << "Rec Chn Error: " << ret;
                return -1;
            }

            auto time_end = std::chrono::steady_clock::now();
            double cost_time = std::chrono::duration_cast<std::chrono::milliseconds>(time_end - time_start).count();

            if(count > 0)
            {
	        vecCost.emplace_back(cost_time);
	    }

            if (count > 0) { cost_time_all += cost_time;}
            count++;
            std::stringstream  info;
            info<< cost_time << "ms " << img_path_concat << ", ";
            BOOST_LOG_TRIVIAL(debug) << info.str();
        }
    }
    std::cout << "cost time : " << cost_time_all << " ,coutn : " << count << std::endl;
    if(count > 1)
    {
	    std::cout << " average time: " << cost_time_all / (count-1) << " ms, total count: " << count<<std::endl;;
    }
    if(vecCost.size() > 0)
    {
        std::sort(vecCost.begin(),vecCost.end());
        std::cout<<"p90 time:"<<vecCost[(int)(0.9*vecCost.size())]<<std::endl;
        std::cout<<"p95 time:"<<vecCost[(int)(0.95*vecCost.size())]<<std::endl;
        std::cout<<"p99 time:"<<vecCost[(int)(0.99*vecCost.size())]<<std::endl;
        std::cout<<"max time:"<< vecCost[vecCost.size()-1]<<std::endl;
    }
    return 0;
}
