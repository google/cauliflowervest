package(default_visibility = ["//cauliflowervest"])

load("@ldap_deps//:requirements.bzl", "package")

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
        "//external:apputils",
        "//external:mock",
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
        package("python-ldap"),
        ":client",
        "//external:apputils",
        "//external:mock",
    ],
)
