#-------------------------------------------------
#
# Project created by QtCreator 2016-01-28T17:25:18
#
#-------------------------------------------------

QT       -= core gui

TARGET = event
TEMPLATE = lib
CONFIG += staticlib

INCLUDEPATH += . ./linux/ ../../../

DEFINES += COMPONENT_BUILD USE_X11=1 \
    USE_SYMBOLIZE USE_OPENSSL=1 USE_GLIB=1 USE_NSS_CERTS=1 \
    __STDC_CONSTANT_MACROS __STDC_FORMAT_MACROS \
    HAVE_CONFIG_H

QMAKE_CFLAGS += -fstack-protector --param=ssp-buffer-size=4 -pthread \
    -fno-strict-aliasing -Wall -Wextra -Wno-unused-parameter \
    -Wno-missing-field-initializers -pipe -fPIC -Wno-unused-variable \
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
    buffer.c \
    evbuffer.c \
    evdns.c \
    event.c \
    event_tagging.c \
    evrpc.c \
    evutil.c \
    http.c \
    log.c \
    poll.c \
    select.c \
    signal.c \
    strlcpy.c \
    epoll.c

HEADERS +=
unix {
    target.path = /usr/lib
    INSTALLS += target
}
