package(default_visibility = ["//cauliflowervest"])

load(
    "//cauliflowervest:builddefs.bzl",
    "cv_appengine_test",
)

py_library(
    name = "errors",
    srcs = ["errors.py"],
)

py_library(
    name = "base",
    srcs = ["base.py"],
    deps = [
        ":errors",
        "//cauliflowervest:settings",
        "//cauliflowervest/server:permissions",
    ],
)

py_library(
    name = "volumes",
    srcs = ["volumes.py"],
    deps = [
        ":base",
        "//cauliflowervest:settings",
        "//cauliflowervest/server:encrypted_property",
        "//cauliflowervest/server:services",
    ],
)

py_library(
    name = "firmware",
    srcs = ["firmware.py"],
    deps = [
        ":base",
        ":errors",
        "//cauliflowervest:settings",
    ],
)

py_library(
    name = "util",
    srcs = ["util.py"],
    deps = [
        ":firmware",
        ":volumes",
    ],
)

py_library(
    name = "models",
    deps = [
        ":base",
        ":firmware",
        ":util",
        ":volumes",
    ],
)

cv_appengine_test(
    name = "base_test",
    size = "small",
    srcs = [
        "base_test.py",
    ],
    deps = [
        ":base",
        "//cauliflowervest/server:settings",
        "//cauliflowervest/server/handlers:test_util",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "volumes_test",
    size = "small",
    srcs = [
        "volumes_test.py",
    ],
    deps = [
        ":models",
        "//cauliflowervest/server:settings",
        "//cauliflowervest/server/handlers:test_util",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

test_suite(
    name = "smoke_tests",
    tests = [
        ":base_test",
        ":volumes_test",
    ],
)
