package(default_visibility = ["//cauliflowervest"])

py_library(
    name = "settings",
    srcs = ["settings.py"],
)

py_library(
    name = "base_client",
    srcs = ["base_client.py"],
    visibility = [
        "//cauliflowervest",
        "//cauliflowervest:cauliflowervest_clients",
    ],
    deps = [
        ":settings",
        ":util",
        "//cauliflowervest:settings",
        "//external:fancy_urllib",
        "//external:oauth2client",
    ],
)

py_library(
    name = "base_flags",
    srcs = ["base_flags.py"],
    deps = [
        ":settings",
        "@absl_git//absl/flags",
    ],
)

py_library(
    name = "util",
    srcs = ["util.py"],
)

# Tests

py_test(
    name = "base_client_test",
    size = "medium",
    srcs = ["base_client_test.py"],
    deps = [
        ":base_client",
        "//external:httplib2",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

py_test(
    name = "util_test",
    size = "small",
    srcs = ["util_test.py"],
    deps = [
        ":util",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

test_suite(
    name = "smoke_tests",
    tests = [
        ":base_client_test",
        ":util_test",
    ],
)

test_suite(
    name = "all_smoke_tests",
    tests = [
        ":smoke_tests",
        "//cauliflowervest/client/mac:all_smoke_tests",
        "//cauliflowervest/client/win:all_smoke_tests",
    ],
)
