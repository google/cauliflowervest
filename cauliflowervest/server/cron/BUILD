package(default_visibility = ["//cauliflowervest"])

load(
    "//cauliflowervest:builddefs.bzl",
    "cv_appengine_test",
)

py_library(
    name = "main",
    srcs = ["main.py"],
    deps = [
        ":group_sync",
        ":inventory_sync",
    ],
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

py_library(
    name = "inventory_sync",
    srcs = ["inventory_sync.py"],
    deps = [
        "//cauliflowervest/server:service_factory",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models:firmware",
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
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "inventory_sync_test",
    srcs = [
        "inventory_sync_test.py",
    ],
    deps = [
        ":inventory_sync",
        ":main",
        "//cauliflowervest/server/handlers:test_util",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

test_suite(
    name = "smoke_tests",
    tests = [
        ":group_sync_test",
        ":inventory_sync_test",
    ],
)

test_suite(
    name = "all_smoke_tests",
    tests = [
        ":smoke_tests",
    ],
)
