package(default_visibility = ["//cauliflowervest"])

load(
    "//cauliflowervest:builddefs.bzl",
    "py_appengine_binary",
    "cv_appengine_test",
)

py_library(
    name = "crypto",
    srcs = ["crypto.py"],
    deps = [
        ":settings",
        "//external:keyczar",
    ],
)

py_library(
    name = "encrypted_property",
    srcs = ["encrypted_property.py"],
    deps = [
        ":crypto",
        ":settings",
        "//common:cloud_kms",
    ],
)

py_library(
    name = "main_lib",
    srcs = ["main.py"],
    data = [
        "//cauliflowervest/server/static:cv_app",
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":settings",
        "//cauliflowervest/server/cron:main",
        "//cauliflowervest/server/handlers:all",
        "//cauliflowervest/server/models:base",
    ],
)

py_library(
    name = "permissions",
    srcs = ["permissions.py"],
)

py_library(
    name = "settings",
    srcs = ["settings.py"],
    deps = [
        ":permissions",
    ],
)

py_library(
    name = "services",
    srcs = ["services.py"],
)

py_library(
    name = "service_factory",
    srcs = ["service_factory.py"],
    deps = [
        ":services",
    ],
)

py_library(
    name = "util",
    srcs = ["util.py"],
    deps = [
        ":crypto",
        ":settings",
        "//cauliflowervest/server/models:base",
    ],
)

py_appengine_binary(
    name = "main",
    srcs = ["main.py"],
    configs = [
        "app.yaml",
        "cron.yaml",
        "index.yaml",
        "queue.yaml",
    ],
    deps = [":main_lib"],
)

# Tests
cv_appengine_test(
    name = "crypto_test",
    size = "small",
    srcs = [
        "crypto_test.py",
    ],
    deps = [
        ":crypto",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "encrypted_property_test",
    size = "small",
    srcs = [
        "encrypted_property_test.py",
    ],
    deps = [
        ":encrypted_property",
        "//cauliflowervest/server/handlers:test_util",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "util_test",
    size = "small",
    srcs = [
        "util_test.py",
    ],
    deps = [
        ":util",
        "//cauliflowervest/server/handlers:test_util",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

test_suite(
    name = "smoke_tests",
    tests = [
        ":crypto_test",
        ":encrypted_property_test",
        ":util_test",
    ],
)

test_suite(
    name = "all_smoke_tests",
    tests = [
        ":smoke_tests",
        "//cauliflowervest/server/cron:smoke_tests",
        "//cauliflowervest/server/handlers:smoke_tests",
        "//cauliflowervest/server/models:smoke_tests",
    ],
)
