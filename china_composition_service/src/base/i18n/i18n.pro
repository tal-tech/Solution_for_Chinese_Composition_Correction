#-------------------------------------------------
#
# Project created by QtCreator 2016-01-29T17:59:40
#
#-------------------------------------------------

QT       -= core gui

TARGET = base_i18n
TEMPLATE = lib

DEFINES += I18N_LIBRARY

INCLUDEPATH += . ../.. ../../third_party/icu/source/i18n \
    ../../third_party/icu/source/common

DEFINES += COMPONENT_BUILD USE_X11=1 \
    USE_SYMBOLIZE USE_OPENSSL=1 USE_GLIB=1 USE_NSS_CERTS=1 \
    __STDC_CONSTANT_MACROS __STDC_FORMAT_MACROS \
    BASE_I18N_IMPLEMENTATION ICU_UTIL_DATA_IMPL=ICU_UTIL_DATA_FILE \
    U_USING_ICU_NAMESPACE=0 U_ENABLE_DYLOAD=0

QMAKE_CXXFLAGS += -fstack-protector --param=ssp-buffer-size=4 -pthread \
    -fno-strict-aliasing -Wall -Wextra -Wno-unused-parameter \
    -Wno-missing-field-initializers -pipe -fPIC \
    -fno-exceptions -fno-rtti -fno-threadsafe-statics \
    -fvisibility-inlines-hidden -std=gnu++11 \
    -Wno-sign-compare -Wno-sign-compare \
    -m64 -march=x86-64

QMAKE_LFLAGS += -Wl,-z,now -Wl,-z,relro -Wl,--fatal-warnings -Wl,-z,defs -pthread \
    -Wl,-z,noexecstack -fPIC -fuse-ld=gold -m64 -Wl,--disable-new-dtags \
    -Wl,--detect-odr-violations -Wl,--icf=all

LIBS += -lrt -ldl

CONFIG(debug, debug|release) {
DEFINES += DYNAMIC_ANNOTATIONS_ENABLED=1 _DEBUG _GLIBCXX_DEBUG=1

QMAKE_CXXFLAGS += -O0 -g

LIBS += -L$$PWD/../../lib/debug -lbase \
    -L$$PWD/../../lib/debug -licuuc -licui18n

DESTDIR = $$PWD/../../lib/debug/
}

CONFIG(release, debug|release) {
DEFINES += NDEBUG NVALGRIND DYNAMIC_ANNOTATIONS_ENABLED=0

QMAKE_CXXFLAGS += -O2

LIBS += -L$$PWD/../../lib/release -lbase \
    -L$$PWD/../../lib/release -licuuc -licui18n

QMAKE_LFLAGS += -Wl,-O1 -Wl,--as-needed -Wl,--gc-sections

DESTDIR = $$PWD/../../lib/release/
}

SOURCES += \
    base_i18n_switches.cc \
    bidi_line_iterator.cc \
    break_iterator.cc \
    case_conversion.cc \
    char_iterator.cc \
    file_util_icu.cc \
    i18n_constants.cc \
    icu_encoding_detection.cc \
    icu_string_conversions.cc \
    icu_util.cc \
    message_formatter.cc \
    number_formatting.cc \
    rtl.cc \
    streaming_utf8_validator.cc \
    string_compare.cc \
    string_search.cc \
    time_formatting.cc \
    timezone.cc \
    utf8_validator_tables.cc

HEADERS += \
    base_i18n_switches.h \
    bidi_line_iterator.h \
    break_iterator.h \
    case_conversion.h \
    char_iterator.h \
    file_util_icu.h \
    i18n_constants.h \
    icu_encoding_detection.h \
    icu_string_conversions.h \
    icu_util.h \
    message_formatter.h \
    number_formatting.h \
    rtl.h \
    streaming_utf8_validator.h \
    string_compare.h \
    string_search.h \
    time_formatting.h \
    timezone.h \
    utf8_validator_tables.h

unix {
    target.path = /usr/lib
    INSTALLS += target
}
