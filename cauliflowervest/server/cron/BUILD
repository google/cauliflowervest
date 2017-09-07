package(default_visibility = ["//cauliflowervest"])

load(
    "//cauliflowervest:builddefs.bzl",
    "cv_appengine_test",
)

py_library(
    name = "all",
    deps = [":group_sync"],
)

py_library(
    name = "group_sync",
    srcs = ["group_sync.py"],
    deps = [
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:settings",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models:base",
    ],
)

# Unit Tests

cv_appengine_test(
    name = "group_sync_test",
    size = "small",
    srcs = [
        "group_sync_test.py",
    ],
    deps = [
        ":group_sync",
        "//cauliflowervest/server/handlers:test_util",
        "//external:apputils",
        "//external:mock",
    ],
)

test_suite(
    name = "smoke_tests",
    tests = [":group_sync_test"],
)

test_suite(
    name = "all_smoke_tests",
    tests = [
        ":smoke_tests",
    ],
)
