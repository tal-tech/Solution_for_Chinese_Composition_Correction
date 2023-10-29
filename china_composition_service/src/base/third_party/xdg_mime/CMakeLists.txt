cmake_minimum_required(VERSION 3.3)
project(xdg_mime)

add_definitions(-D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS)

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
    xdgmime.c
    xdgmimealias.c
    xdgmimecache.c
    xdgmimeglob.c
    xdgmimeicon.c
    xdgmimeint.c
    xdgmimemagic.c
    xdgmimeparent.c
    xdgmime.h
    xdgmimealias.h
    xdgmimecache.h
    xdgmimeglob.h
    xdgmimeicon.h
    xdgmimeint.h
    xdgmimemagic.h
    xdgmimeparent.h)

add_library(xdg_mime STATIC ${SOURCE_FILES})
