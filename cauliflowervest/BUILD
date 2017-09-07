package_group(
    name = "cauliflowervest",
    packages = [
        "//cauliflowervest/...",
    ],
)

package_group(name = "cauliflowervest_clients")

package(default_visibility = [":cauliflowervest"])

py_library(
    name = "settings",
    srcs = ["settings.py"],
    visibility = ["//visibility:public"],
)

# Unit Tests

test_suite(
    name = "all_smoke_tests",
    tests = [
        "//cauliflowervest/client:all_smoke_tests",
        "//cauliflowervest/server:all_smoke_tests",
    ],
)
