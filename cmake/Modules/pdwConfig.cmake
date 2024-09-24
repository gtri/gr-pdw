INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_PDW pdw)

FIND_PATH(
    PDW_INCLUDE_DIRS
    NAMES pdw/api.h
    HINTS $ENV{PDW_DIR}/include
        ${PC_PDW_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    PDW_LIBRARIES
    NAMES gnuradio-pdw
    HINTS $ENV{PDW_DIR}/lib
        ${PC_PDW_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/pdwTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(PDW DEFAULT_MSG PDW_LIBRARIES PDW_INCLUDE_DIRS)
MARK_AS_ADVANCED(PDW_LIBRARIES PDW_INCLUDE_DIRS)
