package(
    default_visibility = [
        "//cauliflowervest",
        "//cauliflowervest:cauliflowervest_clients",
    ],
)

# Libraries
py_library(
    name = "client",
    srcs = ["client.py"],
    deps = [
        ":machine_data",
        "//cauliflowervest:settings",
        "//cauliflowervest/client:base_client",
        "//cauliflowervest/client:util",
    ],
)

py_library(
    name = "glue",
    srcs = ["glue.py"],
    deps = [
        ":storage",
        "//cauliflowervest/client:util",
    ],
)

py_library(
    name = "storage",
    srcs = [
        "apfs.py",
        "corestorage.py",
        "storage.py",
    ],
    deps = [
        "//cauliflowervest/client:util",
    ],
)

py_library(
    name = "machine_data",
    srcs = ["machine_data.py"],
    deps = [
        "//common:hw",
    ],
)

py_library(
    name = "tkinter",
    srcs = ["tkinter.py"],
    deps = [
        ":glue",
        ":storage",
        "//cauliflowervest/client:base_client",
        "//cauliflowervest/client:settings",
        "//cauliflowervest/client:util",
    ],
)

py_library(
    name = "commandline",
    srcs = ["commandline.py"],
    deps = [
        ":glue",
        ":storage",
        "//cauliflowervest/client:base_client",
        "//cauliflowervest/client:settings",
        "//cauliflowervest/client:util",
    ],
)

# Binaries / Genrules / etc.
py_binary(
    name = "cauliflowervest",
    srcs = ["main.py"],
    main = "main.py",
    deps = [
        ":client",
        ":commandline",
        ":glue",
        ":storage",
        ":tkinter",
        "//cauliflowervest:settings",
        "//cauliflowervest/client:base_flags",
        "//cauliflowervest/client:util",
        "@absl_git//absl:app",
    ],
)

# Tests
py_test(
    name = "glue_test",
    size = "small",
    srcs = ["glue_test.py"],
    deps = [
        ":client",
        ":glue",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

py_test(
    name = "corestorage_test",
    size = "small",
    srcs = ["corestorage_test.py"],
    deps = [
        ":storage",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

py_test(
    name = "apfs_test",
    size = "small",
    srcs = ["apfs_test.py"],
    deps = [
        ":storage",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

#  reenable on mac

py_test(
    name = "machine_data_test",
    size = "small",
    srcs = ["machine_data_test.py"],
    deps = [
        ":machine_data",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

test_suite(
    name = "smoke_tests",
    tests = [
        ":apfs_test",
        ":commandline_test",
        ":corestorage_test",
        ":glue_test",
        ":machine_data_test",
    ],
)

test_suite(
    name = "all_smoke_tests",
    tests = [
        ":smoke_tests",
    ],
)

load("@subpar//:subpar.bzl", "par_binary")

par_binary(
    name = "main",
    srcs = ["main.py"],
    deps = [":cauliflowervest"],
)

genrule(
    name = "pkg",
    srcs = [
        "main.par",
        "//common:roots.pem",
    ],
    outs = ["cauliflowervest.pkg"],
    cmd = "if [ `uname` != \"Darwin\" ]; then echo \"\nUnsupported platform. Target have to be build on MacOS.\n\"; exit 1; fi;" +
          "mkdir -p root/usr/local/cauliflowervest/;" +
          "cp $(location main.par) root/usr/local/cauliflowervest/cauliflowervest;" +
          "cp $(location //common:roots.pem) root/usr/local/cauliflowervest/;" +
          "pkgbuild --root=root --identifier cauliflowervest $@",
)
