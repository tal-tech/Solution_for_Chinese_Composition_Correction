cmake_minimum_required(VERSION 3.3)
project(modp_b64)

include_directories(../../)

add_definitions(-D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fstack-protector \
    --param=ssp-buffer-size=4 -pthread \
    -fno-strict-aliasing -Wall -Wextra -Wno-unused-parameter \
    -Wno-missing-field-initializers -fvisibility=hidden -pipe -fPIC \
    -fno-exceptions -fno-rtti -fno-threadsafe-statics \
    -fvisibility-inlines-hidden -std=gnu++11 \
    -m64 -march=x86-64")

set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -O0 -g \
    -DCOMPONENT_BUILD -DDYNAMIC_ANNOTATIONS_ENABLED=1 \
    -D_DEBUG -D_GLIBCXX_DEBUG=1")

set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O2 \
    -DDYNAMIC_ANNOTATIONS_ENABLED=0 -DNDEBUG -DNVALGRIND")

set(SOURCE_FILES
    modp_b64.cc
    modp_b64.h
    modp_b64_data.h)

add_library(modp_b64 STATIC ${SOURCE_FILES})
