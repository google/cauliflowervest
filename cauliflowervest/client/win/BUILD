package(default_visibility = ["//cauliflowervest"])

load("@pip_deps//:requirements.bzl", "requirement")

py_library(
    name = "client",
    srcs = ["client.py"],
    deps = [
        "//cauliflowervest:settings",
        "//cauliflowervest/client:base_client",
    ],
)

# Excluded from oss test_suite.
# It requires libldap2-dev
py_test(
    name = "bitlocker_ad_sync_test",
    size = "small",
    srcs = ["bitlocker_ad_sync_test.py"],
    deps = [
        ":bitlocker_ad_sync",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
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

py_binary(
    name = "bitlocker_ad_sync",
    srcs = ["bitlocker_ad_sync.py"],
    deps = [
        requirement("python-ldap"),
        ":client",
        "//external:mock",
        "@absl_git//absl:app",
        "@absl_git//absl/flags",
    ],
)
