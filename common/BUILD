package(default_visibility = ["//visibility:public"])

exports_files(
    ["roots.pem"],
)

py_library(
    name = "hw",
    srcs = [
        "hw.py",
    ],
    deps = [
        ":plist",
    ],
)

py_library(
    name = "plist",
    srcs = [
        "plist.py",
    ],
)

py_library(
    name = "cloud_kms",
    srcs = ["cloud_kms.py"],
    deps = [
        "//external:googleapiclient",
        "//external:httplib2",
        "//external:oauth2client",
    ],
)
