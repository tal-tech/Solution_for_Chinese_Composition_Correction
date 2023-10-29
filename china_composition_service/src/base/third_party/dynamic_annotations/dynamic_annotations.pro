#-------------------------------------------------
#
# Project created by QtCreator 2016-01-28T17:15:54
#
#-------------------------------------------------

QT       -= core gui

TARGET = dynamic_annotations
TEMPLATE = lib
CONFIG += staticlib

INCLUDEPATH += . ../../../

DEFINES += COMPONENT_BUILD USE_X11=1 \
    USE_SYMBOLIZE USE_OPENSSL=1 USE_GLIB=1 USE_NSS_CERTS=1 \
    __STDC_CONSTANT_MACROS __STDC_FORMAT_MACROS

QMAKE_CFLAGS += -fstack-protector --param=ssp-buffer-size=4 -pthread \
    -fno-strict-aliasing -Wall -Wextra -Wno-unused-parameter \
    -Wno-missing-field-initializers -fvisibility=hidden -pipe -fPIC \
    -m64 -march=x86-64

CONFIG(debug, debug|release) {
DEFINES += DYNAMIC_ANNOTATIONS_ENABLED=1 _DEBUG _GLIBCXX_DEBUG=1

QMAKE_CXXFLAGS += -O0 -g

DESTDIR = $$OUT_PWD/../../../lib/debug/
}

CONFIG(release, debug|release) {
DEFINES += NDEBUG NVALGRIND DYNAMIC_ANNOTATIONS_ENABLED=0

QMAKE_CXXFLAGS += -O2

DESTDIR = $$OUT_PWD/../../../lib/release/
}

!defined(TCMALLOC, var) {
DEFINES += NO_TCMALLOC
}

SOURCES += \
    dynamic_annotations.c

HEADERS += \
    dynamic_annotations.h
unix {
    target.path = /usr/lib
    INSTALLS += target
}

