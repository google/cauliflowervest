package(default_visibility = ["//cauliflowervest"])

py_library(
    name = "client",
    srcs = ["client.py"],
    visibility = [
        "//cauliflowervest",
        "//cauliflowervest:cauliflowervest_clients",
    ],
    deps = [
        "//cauliflowervest:settings",
        "//cauliflowervest/client:base_client",
    ],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    deps = [
        ":client",
        "//cauliflowervest/client:base_client",
        "//cauliflowervest/client:base_flags",
        "@absl_git//absl:app",
    ],
)
