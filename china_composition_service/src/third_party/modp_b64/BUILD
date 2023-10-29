licenses(["notice"])
package(default_visibility = ["//visibility:public"])
cc_library(name = "modp_b64",
    srcs = [
        "modp_b64.cc",
    ],
    hdrs = [
        "modp_b64.h", 
        "modp_b64_data.h",
    ],
    copts = [
        "-Ithird_party/chromium",
        "-Bthird_party/chromium/third_party/binutils/Linux_x64/Release/bin",
        "-DCOMPONENT_BUILD",
        "-DBASE_IMPLEMENTATION",
        "-DUSE_X11=1",
        "-DUSE_SYMBOLIZE",
        "-DUSE_OPENSSL=1",
        "-DUSE_GLIB=1",
        "-DUSE_NSS_CERTS=1",
        "-D__STDC_CONSTANT_MACROS",
        "-D__STDC_FORMAT_MACROS",
        "-m64",
        "-march=x86-64",
    ],
)
