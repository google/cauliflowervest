package(default_visibility = ["//cauliflowervest"])

py_library(
    name = "client",
    srcs = ["client.py"],
    deps = [
        "//cauliflowervest:settings",
        "//cauliflowervest/client:base_client",
    ],
)

test_suite(
    name = "smoke_tests",
    tests = [
    ],
)

test_suite(
    name = "all_smoke_tests",
    tests = [
        ":smoke_tests",
    ],
)
