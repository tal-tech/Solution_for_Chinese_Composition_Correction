cmake_minimum_required(VERSION 3.3)
project(event)


include_directories(./linux/ ../../../)

add_definitions(-D__STDC_CONSTANT_MACROS
        -D__STDC_FORMAT_MACROS
        -DHAVE_CONFIG_H)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fstack-protector \
    --param=ssp-buffer-size=4 -pthread \
    -fno-strict-aliasing -Wall -Wextra -Wno-unused-parameter \
    -Wno-missing-field-initializers -fvisibility=hidden -pipe -fPIC \
    -m64 -march=x86-64")

set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -O0 -g \
    -DCOMPONENT_BUILD -DDYNAMIC_ANNOTATIONS_ENABLED=1 \
    -D_DEBUG -D_GLIBCXX_DEBUG=1")

set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O2 \
    -DDYNAMIC_ANNOTATIONS_ENABLED=0 -DNDEBUG -DNVALGRIND")

set(SOURCE_FILES
        buffer.c
        evbuffer.c
        evdns.c
        event.c
        event_tagging.c
        evrpc.c
        evutil.c
        http.c
        log.c
        poll.c
        select.c
        signal.c
        strlcpy.c
        epoll.c)

add_library(event STATIC ${SOURCE_FILES})
