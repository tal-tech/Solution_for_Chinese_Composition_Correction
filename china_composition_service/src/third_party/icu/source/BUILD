licenses(["notice"])

cc_library(
    name = "icu",
    srcs = [
        "lib/libicuuc.so",
    ],
    copts = [
        "-Ithird_party/chromium/third_party/icu/source",
    ],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "icu_debug",
    srcs = [
        "lib/libicuuc_debug.so",
    ],
    copts = [
        "-Ithird_party/chromium/third_party/icu/source",
    ],
    visibility = ["//visibility:public"],
)
