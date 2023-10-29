cmake_minimum_required(VERSION 3.6)
project(eureka)


set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 ")
set(SOURCE_FILES eureka_client.cpp eureka_client.h)

add_library(eureka SHARED ${SOURCE_FILES})

link_directories(lib)

TARGET_LINK_LIBRARIES(eureka jsoncpp curl -lcrypt -lnsl -lpthread -lrt -ldl)
