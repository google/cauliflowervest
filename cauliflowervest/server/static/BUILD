package(default_visibility = ["//visibility:public"])

load("@io_bazel_rules_closure//closure:defs.bzl", "web_library")

web_library(
    name = "ts1",
    srcs = [
        "index.html",
    ],
    path = "/",
    deps = [
        "//cauliflowervest/server/frontend:cauliflowervest_app_webfiles",
        "@org_polymer_webcomponentsjs",
    ],
)

load("@org_tensorflow_tensorboard//tensorboard/defs:vulcanize.bzl", "tensorboard_html_binary")

tensorboard_html_binary(
    name = "cv_app",
    compilation_level = "SIMPLE",
    input_path = "/index.html",
    output_path = "/out.html",
    deps = [
        ":ts1",
    ],
)
