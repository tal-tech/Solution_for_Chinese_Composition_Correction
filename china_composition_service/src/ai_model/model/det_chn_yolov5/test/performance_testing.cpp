#include "det_chn_yolov5.hpp"
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

    setupLog("det_chn_yolov5_performance.log");
    const std::string det1_model = argv[1];
    const std::string images_folder = argv[2];
    const std::string config_file = argv[3];
    int repeat_count = argc > 4 ? std::stoi(argv[4]) : 1;

    std::cout << "running ... ,please wait" << std::endl;
    DetChnYolo *area_detector = DetChnYolo::create(
            det1_model,
            config_file);
    std::cout << "load over" << std::endl;
    double cost_time_all = 0.0;
    int count = 0;
    double predict_used_all = 0.0;
    double post_used_all = 0.0;
    std::vector<double> vecCost;
    for (int i = 0; repeat_count <= 0 || i < repeat_count; i++) {
	vecCost.clear();
        std::vector<std::string> imgs_path = getFilePath(images_folder);
        //std::vector<std::string> imgs_path = {"./test_images/two_162.jpg","./test_images/one_369.jpg"};
        for (int i = 0; i < imgs_path.size(); i++)
        {
            std::string img_path = imgs_path[i];
            int pos = img_path.find_last_of('/');
            cout << img_path<<": ";
            std::string image_name =  img_path.substr(pos + 1, img_path.size() - pos);
            cv::Mat img = cv::imread(img_path);
            if (img.data == 0 || img.rows <= 0 || img.cols <= 0) {
                BOOST_LOG_TRIVIAL(error) << "read image failed:" << img_path;
                continue;
            }
            std::vector<cv::Mat> input_imgs;

            int batch_size = 1;
            for (int i = 0 ; i < batch_size; i++) {
                input_imgs.push_back(img);
            }
            auto time_start = std::chrono::steady_clock::now();
            std::vector<std::vector<float>> final_boxes;

            double predict_used = 0;
            double post_used = 0;
            int ret = area_detector->detection(input_imgs,final_boxes,predict_used, post_used,false);
	    if(count > 0)
	    {
                predict_used_all += predict_used;
                post_used_all += post_used;
	    }
            for (auto r : final_boxes) {
                std::cout <<"####" << r[1] << " , " << r[2] << " , " << r[3] << " , " << r[4] << " , " << r[5] << std::endl;
            }
            if (ret < 0) {
                BOOST_LOG_TRIVIAL(info) << "Error: " << ret;
                return -1;
            }
                /*
                ofstream out(string("./txt_result/") +image_name+ ".txt", ios::out | ios::app);

                cv::Mat showMat = input_imgs[0].clone();
                cv::Mat showMatSrc = input_imgs[0].clone();

                vector<cv::Scalar> colors = {cv::Scalar(255,0,0), cv::Scalar(0,255,0),  cv::Scalar(0,0,255), cv::Scalar(255,255,0), cv::Scalar(255,0,255), cv::Scalar(0,255,255)} ;
                std::cout << "final_boxes " << endl;
                for (int i = 0; i < final_boxes.size(); i++){
                    cv::Scalar color = colors[i%colors.size()];
                    rectangle(showMatSrc, final_boxes[i], color, 2, 2, 0);
                    cv::putText(showMatSrc, std::to_string(i), cv::Point(final_boxes[i].x +final_boxes[i].width/2, final_boxes[i].y + final_boxes[i].height/2), cv::FONT_HERSHEY_COMPLEX, 1, color, 1, 1, 0);
                    int x0 = final_boxes[i].x;
                    int y0 = final_boxes[i].y;
                    int x1 = final_boxes[i].x + final_boxes[i].width;
                    int y1 = final_boxes[i].y + final_boxes[i].height;
                    std::cout << x0 << " " << y0 << " " <<  x1 << " " << y1 << endl;
                    //final_boxes[i].x << " " << final_boxes[i].y << " "<< final_boxes[i].x + final_boxes[i].width<< " " << final_boxes[i].y + final_boxes[i].height << " 1.0" << endl;
                    rectangle(showMat, final_show_boxes[i], color, 2, 2, 0);
                    cv::putText(showMat, std::to_string(i), cv::Point(final_show_boxes[i].x +final_show_boxes[i].width/2, final_show_boxes[i].y + final_show_boxes[i].height/2), cv::FONT_HERSHEY_COMPLEX, 1,color, 1, 1, 0);
                    
                    out << "2," <<  x0 << "," << y0 << "," << x1 << "," << y0 << "," <<  x1 << "," << y1 << "," << x0 << "," << y1 << ",1.0" << endl;

                }

            circle(showMat, cv::Point(anchor[0], anchor[1]), 20, cv::Scalar(120, 120, 120), -1);	
            circle(showMatSrc, cv::Point(anchor[0], anchor[1]), 20, cv::Scalar(120, 120, 120), -1);

            rectangle(showMat, anchor_show_box, cv::Scalar(50,50,50), 3, 3, 0);
            rectangle(showMatSrc, anchor_box, cv::Scalar(50,50,50), 3, 3, 0);

            cv::imwrite("./show/"+image_name, showMat);
            cv::imwrite("./show/"+image_name+"_src.jpg", showMatSrc);
            */
            auto time_end = std::chrono::steady_clock::now();
            double cost_time = std::chrono::duration_cast<std::chrono::milliseconds>(time_end - time_start).count();
            // std::cout<<cost_time<<std::endl;
	    if(count > 0)
	    {
	        vecCost.emplace_back(cost_time);
	    }
            if (count > 0) { cost_time_all += cost_time; }
            count++;
            std::stringstream  info;

            info<< cost_time << "ms " << img_path << " ";

            BOOST_LOG_TRIVIAL(info) << info.str();
       
        }
    }
    if(count > 1)
    {
        cout << " average time: " << cost_time_all / (count-1) << " ms"<<std::endl;
    }
    if(vecCost.size() > 0)
    { 
        std::sort(vecCost.begin(),vecCost.end());
        std::cout<<"p90 time:"<<vecCost[(int)(0.9*vecCost.size())]<<std::endl;
	std::cout<<"p95 time:"<<vecCost[(int)(0.95*vecCost.size())]<<std::endl;
        std::cout<<"p99 time:"<<vecCost[(int)(0.99*vecCost.size())]<<std::endl;
	std::cout<<"max time:"<< vecCost[vecCost.size()-1]<<std::endl;
    }
    if(count > 1)
    {
        cout << "avg predict time : " << predict_used_all / (count-1) << " ms"<<std::endl;
        cout << "avg post time : " << post_used_all / (count-1) << " ms"<<std::endl;
    }
    
    return 0;
}
