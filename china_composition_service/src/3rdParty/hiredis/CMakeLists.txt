CMAKE_MINIMUM_REQUIRED(VERSION 3.0.0)
INCLUDE(GNUInstallDirs)

MACRO(getVersionBit name)
  SET(VERSION_REGEX "^#define ${name} (.+)$")
  FILE(STRINGS "hiredis.h"
    VERSION_BIT REGEX ${VERSION_REGEX})
  STRING(REGEX REPLACE ${VERSION_REGEX} "\\1" ${name} "${VERSION_BIT}")
ENDMACRO(getVersionBit)

getVersionBit(HIREDIS_MAJOR)
getVersionBit(HIREDIS_MINOR)
getVersionBit(HIREDIS_PATCH)
getVersionBit(HIREDIS_SONAME)
SET(VERSION "${HIREDIS_MAJOR}.${HIREDIS_MINOR}.${HIREDIS_PATCH}")
MESSAGE("Detected version: ${VERSION}")

PROJECT(hiredis VERSION "${VERSION}")

SET(ENABLE_EXAMPLES OFF CACHE BOOL "Enable building hiredis examples")

INCLUDE_DIRECTORIES(../../..)

ADD_LIBRARY(hiredis SHARED
        async.c
        dict.c
        hiredis.c
        net.c
        read.c
        sds.c)

SET_TARGET_PROPERTIES(hiredis
    PROPERTIES
    VERSION "${HIREDIS_SONAME}")

#CONFIGURE_FILE(hiredis.pc.in hiredis.pc @ONLY)
#
#INSTALL(TARGETS hiredis
#    DESTINATION "${CMAKE_INSTALL_LIBDIR}")
#
#INSTALL(FILES hiredis.h read.h sds.h async.h
#    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/hiredis)
#
#INSTALL(FILES ${CMAKE_CURRENT_BINARY_DIR}/hiredis.pc
#    DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig)
#
#ADD_EXECUTABLE(hiredis-test
#    test.c)
#TARGET_LINK_LIBRARIES(hiredis-test hiredis)

