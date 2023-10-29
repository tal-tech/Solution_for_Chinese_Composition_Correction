cmake_minimum_required(VERSION 3.10)

project(Evaluation)
set(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/package")
#set(PACKVERSION 2.0.0.1)
######################################################################
#全局编译标志
######################################################################
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x -g")  

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")

set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -O0")

set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O2")

set(CUDA_cublas_device_LIBRARY /usr/local/cuda/lib64)
######################################################################
#全局链接和包含
######################################################################

include_directories(${PROJECT_SOURCE_DIR})
include_directories(${CMAKE_SOURCE_DIR}/3rdParty/mysql_connector/include/jdbc)
include_directories(${CMAKE_SOURCE_DIR}/3rdParty/ali_oss/include)
include_directories(${CMAKE_SOURCE_DIR}/3rdParty)
include_directories(${CMAKE_SOURCE_DIR}/common)
include_directories(${CMAKE_SOURCE_DIR}/3rdParty/redis_sds/include)

include_directories(${CMAKE_SOURCE_DIR}/ai_model)
include_directories(${CMAKE_SOURCE_DIR}/ai_model/include)
include_directories(${CMAKE_SOURCE_DIR}/ai_model/include/opencv)

link_directories(${CMAKE_SOURCE_DIR}/ai_model/lib)
link_directories(${CMAKE_SOURCE_DIR}/3rdParty/eureka/lib)
link_directories(${CMAKE_SOURCE_DIR}/3rdParty/librdkafka/lib)
link_directories(${CMAKE_SOURCE_DIR}/3rdParty/ubuntu-cuda10)

link_directories(${CMAKE_SOURCE_DIR}/3rdParty/mysql_connector/lib)
link_directories(${CMAKE_SOURCE_DIR}/3rdParty/ali_oss/lib)
link_directories(${CMAKE_SOURCE_DIR}/3rdParty/redis_sds/lib)
#link_directories(${CMAKE_SOURCE_DIR}/3rdParty/opencv/lib)
#find_package(Boost REQUIRED)
#if (Boost_FOUND)
#    include_directories(${Boost_INCLUDE_DIRS})
#    link_directories(${Boost_LIBRARIES})
#endif()

# set(Torch_DIR ${CMAKE_SOURCE_DIR}/ai_model/libtorch/share/cmake/Torch)
# find_package(Torch REQUIRED)
# if (Torch_FOUND)
#     include_directories(${Torch_INCLUDE_DIRS})
#     link_directories(${Torch_LIBRARIES})
#     message(STATUS "Torch library status:")
#     message(STATUS "    libraries: ${TORCH_LIBRARIES}")
#     message(STATUS "    include path: ${Torch_INCLUDE_DIRS}")
# endif()

#################################################################L#####
#全局编译输出指定
######################################################################

#IF(CMAKE_BUILD_TYPE MATCHES Debug)
set(CMAKE_VERBOSE_MAKEFILE ON)
#ENDIF(CMAKE_BUILD_TYPE MATCHES Debug)

string(TOLOWER ${CMAKE_BUILD_TYPE} BUILD_TYPE)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib/${BUILD_TYPE})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin/${BUILD_TYPE})


######################################################################
#子工程目录
######################################################################
add_subdirectory(base/third_party/dynamic_annotations)
add_subdirectory(base/third_party/symbolize)
add_subdirectory(base/third_party/xdg_mime)
add_subdirectory(base/third_party/libevent)
add_subdirectory(third_party)
add_subdirectory(base)
add_subdirectory(3rdParty/eureka)
add_subdirectory(breakpad)
add_subdirectory(3rdParty/hiredis)

include_directories(${PROJECT_SOURCE_DIR}/breakpad/src)
include_directories(${PROJECT_SOURCE_DIR}/3rdParty/eureka)


######################################################################
#common目录 获取所有源文件
######################################################################
aux_source_directory(${CMAKE_SOURCE_DIR}/common DIR_COMMON_SRCS)
aux_source_directory(${CMAKE_SOURCE_DIR}/ai_model/src DIR_MODEL_SRCS)
######################################################################
#编译对象
######################################################################

add_executable(Evaluation
    service_main.cpp
    init_server.cpp
    image_operation.cpp
    tal_interface.cpp
    image_interface.cpp
    app.cpp
    ${DIR_COMMON_SRCS}
    ${DIR_MODEL_SRCS}
    ai_model/composion.cpp
    url_request.cpp
)



target_link_libraries(Evaluation
        opencv_core
        opencv_imgproc
        opencv_imgcodecs
		cudnn
        jsoncpp
        breakpad_client
        base
        curl
        eureka
        rdkafka
        cppkafka
        sds
        alibabacloud-oss-cpp-sdk
        hiredis
        mysqlcppconn
        ssl
        crypto
        boost_system

        det_chn_comp
        rec_chn_comp
        det_timu_yolov5
    )

######################################################################
#程序发布设置
######################################################################

install(DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/ DESTINATION bin)
install(DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/ DESTINATION lib)
install(DIRECTORY 3rdParty/ali_oss/lib DESTINATION .)
install(DIRECTORY 3rdParty/mysql_connector/lib DESTINATION .)
install(DIRECTORY 3rdParty/redis_sds/lib DESTINATION .)
install(DIRECTORY 3rdParty/librdkafka/lib DESTINATION .)
install(DIRECTORY 3rdParty/eureka/lib DESTINATION .)
#install(DIRECTORY 3rdParty/opencv/lib DESTINATION .)
install(DIRECTORY config/ DESTINATION bin/config)
install(DIRECTORY 3rdParty/ubuntu-cuda10 DESTINATION lib)
install(DIRECTORY ai_model/lib DESTINATION .)
install(DIRECTORY ai_model/model DESTINATION .)
