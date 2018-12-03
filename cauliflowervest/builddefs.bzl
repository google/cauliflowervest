"""Abstraction layer for build rules."""

load("@io_bazel_rules_appengine//appengine:py_appengine.bzl", "py_appengine_binary", "py_appengine_test")
load("@io_bazel_rules_closure//closure:defs.bzl", "web_library")
load("@pip_deps//:requirements.bzl", "requirement")

def cv_appengine_test(name, srcs, deps = [], data = [], size = "medium"):  # pylint: disable=unused-argument
    py_appengine_test(
        name = name,
        srcs = srcs,
        deps = deps + [
            requirement("pillow"),
            requirement("pycrypto"),
        ],
        data = data,
        libraries = {
            "jinja2": "latest",
            "webapp2": "latest",
            "yaml": "latest",
        },
    )

def webcomponent_library(
        name,
        srcs,
        deps = [],
        data = [],
        destdir = "",
        strip_prefix = None,
        suppress = ["*"],
        extra_webfiles_srcs = [],
        exports = None,
        visibility = None,
        deprecation = None,
        testonly = None,
        compatible_with = None):
    """Wrapper on top of web_library."""
    path = "/" + destdir
    webfiles_srcs = depset(srcs + extra_webfiles_srcs).to_list()
    web_library(
        name = name,
        path = path,
        srcs = webfiles_srcs,
        data = data,
        deps = deps,
        exports = exports,
        suppress = suppress,
        strip_prefix = strip_prefix,
        visibility = visibility,
        deprecation = deprecation,
        testonly = testonly,
        compatible_with = compatible_with,
    )

    native.alias(
        name = name + "_webfiles",
        actual = ":" + name,
    )
