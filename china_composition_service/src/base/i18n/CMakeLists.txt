cmake_minimum_required(VERSION 3.3)
project(base_i18n)

include_directories(../../
        ../../third_party/icu/source/i18n
        ../../third_party/icu/source/common)

add_definitions(
        -DUSE_SYMBOLIZE
        -DUSE_GLIB=1
        -D__STDC_CONSTANT_MACROS
        -D__STDC_FORMAT_MACROS
        -DICU_UTIL_DATA_IMPL=ICU_UTIL_DATA_FILE
        -DU_USING_ICU_NAMESPACE=0
        -DU_ENABLE_DYLOAD=0
        -DBASE_I18N_IMPLEMENTATION)

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

set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} \
    -Wl,-z,now -Wl,-z,relro -Wl,--fatal-warnings -Wl,-z,defs -pthread \
    -Wl,-z,noexecstack -fPIC -fuse-ld=gold -m64 -Wl,--disable-new-dtags \
    -Wl,--detect-odr-violations -Wl,--icf=all")

#IF(CMAKE_BUILD_TYPE MATCHES Debug)
#    link_directories(../../third_party/x86_64-linux-gnu/lib/debug)
#ELSE(CMAKE_BUILD_TYPE MATCHES Debug)
#    link_directories(../../third_party/x86_64-linux-gnu/lib/release)
#    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} \
#        -Wl,-O1 -Wl,--as-needed -Wl,--gc-sections")
#ENDIF(CMAKE_BUILD_TYPE MATCHES Debug)


set(SOURCE_FILES
        base_i18n_switches.cc
        bidi_line_iterator.cc
        break_iterator.cc
        case_conversion.cc
        char_iterator.cc
        file_util_icu.cc
        i18n_constants.cc
        icu_encoding_detection.cc
        icu_string_conversions.cc
        icu_util.cc
        message_formatter.cc
        number_formatting.cc
        rtl.cc
        streaming_utf8_validator.cc
        string_compare.cc
        string_search.cc
        time_formatting.cc
        timezone.cc
        utf8_validator_tables.cc
        base_i18n_switches.h
        bidi_line_iterator.h
        break_iterator.h
        case_conversion.h
        char_iterator.h
        file_util_icu.h
        i18n_constants.h
        icu_encoding_detection.h
        icu_string_conversions.h
        icu_util.h
        message_formatter.h
        number_formatting.h
        rtl.h
        streaming_utf8_validator.h
        string_compare.h
        string_search.h
        time_formatting.h
        timezone.h
        utf8_validator_tables.h)

IF(CMAKE_BUILD_TYPE MATCHES Debug)
    add_library(base_i18n SHARED ${SOURCE_FILES})
    target_link_libraries(base_i18n base icuuc icui18n rt dl)
ELSE(CMAKE_BUILD_TYPE MATCHES Debug)
    add_library(base_i18n STATIC ${SOURCE_FILES})
    add_dependencies(base_i18n
            base
            icuuc
            icui18n)
ENDIF(CMAKE_BUILD_TYPE MATCHES Debug)
