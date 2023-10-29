#-------------------------------------------------
#
# Project created by QtCreator 2016-01-28T16:47:22
#
#-------------------------------------------------

QT       -= core gui

TARGET = modp_b64
TEMPLATE = lib
CONFIG += staticlib

INCLUDEPATH += . ../../

DEFINES += COMPONENT_BUILD USE_X11=1 \
    USE_SYMBOLIZE USE_OPENSSL=1 USE_GLIB=1 USE_NSS_CERTS=1 \
    __STDC_CONSTANT_MACROS __STDC_FORMAT_MACROS

QMAKE_CXXFLAGS += -fstack-protector --param=ssp-buffer-size=4 -Werror -pthread \
    -fno-strict-aliasing -Wall -Wextra -Wno-unused-parameter \
    -Wno-missing-field-initializers -fvisibility=hidden -pipe -fPIC \
    -fno-exceptions -fno-rtti -fno-threadsafe-statics \
    -fvisibility-inlines-hidden -std=gnu++11 \
    -m64 -march=x86-64

CONFIG(debug, debug|release) {
DEFINES += DYNAMIC_ANNOTATIONS_ENABLED=1 _DEBUG _GLIBCXX_DEBUG=1

QMAKE_CXXFLAGS += -O0 -g

DESTDIR = $$OUT_PWD/../../lib/debug/
}

CONFIG(release, debug|release) {
DEFINES += NDEBUG NVALGRIND DYNAMIC_ANNOTATIONS_ENABLED=0

QMAKE_CXXFLAGS += -O2

DESTDIR = $$OUT_PWD/../../lib/release/
}

!defined(TCMALLOC, var) {
DEFINES += NO_TCMALLOC
}

SOURCES += \
    modp_b64.cc

HEADERS += \
    modp_b64.h \
    modp_b64_data.h
unix {
    target.path = /usr/lib
    INSTALLS += target
}
