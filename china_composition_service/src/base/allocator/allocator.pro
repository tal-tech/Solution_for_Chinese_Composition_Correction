#-------------------------------------------------
#
# Project created by QtCreator 2016-01-28T17:43:52
#
#-------------------------------------------------

QT       -= core gui

TARGET = allocator
TEMPLATE = lib
CONFIG += staticlib

INCLUDEPATH += . ../../base/allocator \
    ../../third_party/tcmalloc/chromium/src/base \
    ../../third_party/tcmalloc/chromium/src ../../

DEFINES += COMPONENT_BUILD USE_X11=1 \
    USE_SYMBOLIZE USE_OPENSSL=1 USE_GLIB=1 USE_NSS_CERTS=1 \
    __STDC_CONSTANT_MACROS __STDC_FORMAT_MACROS \
    NO_HEAP_CHECK TCMALLOC_FOR_DEBUGALLOCATION

QMAKE_CXXFLAGS += -fstack-protector --param=ssp-buffer-size=4 -pthread \
    -fno-strict-aliasing -Wall -Wextra -Wno-unused-parameter \
    -Wno-missing-field-initializers -pipe -fPIC \
    -fno-exceptions -fno-rtti -fno-threadsafe-statics \
    -fvisibility-inlines-hidden -std=gnu++11 \
    -Wno-sign-compare -Wno-sign-compare \
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

SOURCES += \
    ../../third_party/tcmalloc/chromium/src/base/abort.cc \
    ../../third_party/tcmalloc/chromium/src/base/atomicops-internals-x86.cc \
    ../../third_party/tcmalloc/chromium/src/base/elf_mem_image.cc \
    ../../third_party/tcmalloc/chromium/src/base/linuxthreads.cc \
    ../../third_party/tcmalloc/chromium/src/base/logging.cc \
    ../../third_party/tcmalloc/chromium/src/base/low_level_alloc.cc \
    ../../third_party/tcmalloc/chromium/src/base/spinlock.cc \
    ../../third_party/tcmalloc/chromium/src/base/spinlock_internal.cc \
    ../../third_party/tcmalloc/chromium/src/base/sysinfo.cc \
    ../../third_party/tcmalloc/chromium/src/base/vdso_support.cc \
    ../../third_party/tcmalloc/chromium/src/central_freelist.cc \
    ../../third_party/tcmalloc/chromium/src/common.cc \
    ../../third_party/tcmalloc/chromium/src/free_list.cc \
    ../../third_party/tcmalloc/chromium/src/heap-profiler.cc \
    ../../third_party/tcmalloc/chromium/src/heap-profile-table.cc \
    ../../third_party/tcmalloc/chromium/src/internal_logging.cc \
    ../../third_party/tcmalloc/chromium/src/malloc_extension.cc \
    ../../third_party/tcmalloc/chromium/src/malloc_hook.cc \
    ../../third_party/tcmalloc/chromium/src/maybe_threads.cc \
    ../../third_party/tcmalloc/chromium/src/memory_region_map.cc \
    ../../third_party/tcmalloc/chromium/src/page_heap.cc \
    ../../third_party/tcmalloc/chromium/src/raw_printer.cc \
    ../../third_party/tcmalloc/chromium/src/sampler.cc \
    ../../third_party/tcmalloc/chromium/src/span.cc \
    ../../third_party/tcmalloc/chromium/src/stack_trace_table.cc \
    ../../third_party/tcmalloc/chromium/src/stacktrace.cc \
    ../../third_party/tcmalloc/chromium/src/static_vars.cc \
    ../../third_party/tcmalloc/chromium/src/symbolize.cc \
    ../../third_party/tcmalloc/chromium/src/system-alloc.cc \
    debugallocation_shim.cc \
    ../../third_party/tcmalloc/chromium/src/thread_cache.cc

HEADERS += \
    ../../third_party/tcmalloc/chromium/src/base/abort.h \
    ../../third_party/tcmalloc/chromium/src/base/atomicops-internals-x86.h \
    ../../third_party/tcmalloc/chromium/src/base/elf_mem_image.h \
    ../../third_party/tcmalloc/chromium/src/base/linuxthreads.h \
    ../../third_party/tcmalloc/chromium/src/base/logging.h \
    ../../third_party/tcmalloc/chromium/src/base/low_level_alloc.h \
    ../../third_party/tcmalloc/chromium/src/base/simple_mutex.h \
    ../../third_party/tcmalloc/chromium/src/base/spinlock.h \
    ../../third_party/tcmalloc/chromium/src/base/spinlock_internal.h \
    ../../third_party/tcmalloc/chromium/src/base/sysinfo.h \
    ../../third_party/tcmalloc/chromium/src/base/vdso_support.h \
    ../../third_party/tcmalloc/chromium/src/central_freelist.h \
    ../../third_party/tcmalloc/chromium/src/common.h \
    ../../third_party/tcmalloc/chromium/src/free_list.h \
    ../../third_party/tcmalloc/chromium/src/heap-profile-stats.h \
    ../../third_party/tcmalloc/chromium/src/heap-profile-table.h \
    ../../third_party/tcmalloc/chromium/src/internal_logging.h \
    ../../third_party/tcmalloc/chromium/src/maybe_threads.h \
    ../../third_party/tcmalloc/chromium/src/memory_region_map.h \
    ../../third_party/tcmalloc/chromium/src/page_heap.h \
    ../../third_party/tcmalloc/chromium/src/raw_printer.h \
    ../../third_party/tcmalloc/chromium/src/sampler.h \
    ../../third_party/tcmalloc/chromium/src/span.h \
    ../../third_party/tcmalloc/chromium/src/stack_trace_table.h \
    ../../third_party/tcmalloc/chromium/src/static_vars.h \
    ../../third_party/tcmalloc/chromium/src/symbolize.h \
    ../../third_party/tcmalloc/chromium/src/system-alloc.h \
    ../../third_party/tcmalloc/chromium/src/thread_cache.h
unix {
    target.path = /usr/lib
    INSTALLS += target
}
