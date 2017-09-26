git_repository(
    name = "subpar",
    remote = "https://github.com/google/subpar",
    tag = "1.0.0",
)

git_repository(
    name = "io_bazel_rules_appengine",
    commit = "9df1e255717585fce07551729aad625d5505ac50",
    remote = "https://github.com/bazelbuild/rules_appengine.git",
)

load("@io_bazel_rules_appengine//appengine:py_appengine.bzl", "py_appengine_repositories")

py_appengine_repositories()

# needed for mock, webtest
new_http_archive(
    name = "six_archive",
    build_file = "//third_party:six.BUILD",
    sha256 = "105f8d68616f8248e24bf0e9372ef04d3cc10104f1980f54d57b2ce73a5ad56a",
    strip_prefix = "six-1.10.0",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/source/s/six/six-1.10.0.tar.gz",
        "http://pypi.python.org/packages/source/s/six/six-1.10.0.tar.gz",
    ],
)

bind(
    name = "six",
    actual = "@six_archive//:six",
)

new_http_archive(
    name = "mock_archive",
    build_file = "//third_party:mock.BUILD",
    sha256 = "b839dd2d9c117c701430c149956918a423a9863b48b09c90e30a6013e7d2f44f",
    strip_prefix = "mock-1.0.1",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/a2/52/7edcd94f0afb721a2d559a5b9aae8af4f8f2c79bc63fdbe8a8a6c9b23bbe/mock-1.0.1.tar.gz",
        "https://pypi.python.org/packages/a2/52/7edcd94f0afb721a2d559a5b9aae8af4f8f2c79bc63fdbe8a8a6c9b23bbe/mock-1.0.1.tar.gz",
    ],
)

bind(
    name = "mock",
    actual = "@mock_archive//:mock",
)

bind(
    name = "webob",
    actual = "@com_google_appengine_python//:webob-latest",
)

# needed for webtest
new_http_archive(
    name = "waitress_archive",
    build_file = "//third_party:waitress.BUILD",
    sha256 = "c74fa1b92cb183d5a3684210b1bf0a0845fe8eb378fa816f17199111bbf7865f",
    strip_prefix = "waitress-1.0.2",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/cd/f4/400d00863afa1e03618e31fd7e2092479a71b8c9718b00eb1eeb603746c6/waitress-1.0.2.tar.gz",
        "https://pypi.python.org/packages/cd/f4/400d00863afa1e03618e31fd7e2092479a71b8c9718b00eb1eeb603746c6/waitress-1.0.2.tar.gz",
    ],
)

bind(
    name = "waitress",
    actual = "@waitress_archive//:waitress",
)

# needed for webtest
new_http_archive(
    name = "beautifulsoup4_archive",
    build_file = "//third_party:beautifulsoup4.BUILD",
    sha256 = "b21ca09366fa596043578fd4188b052b46634d22059e68dd0077d9ee77e08a3e",
    strip_prefix = "beautifulsoup4-4.5.3",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/9b/a5/c6fa2d08e6c671103f9508816588e0fb9cec40444e8e72993f3d4c325936/beautifulsoup4-4.5.3.tar.gz",
        "https://pypi.python.org/packages/9b/a5/c6fa2d08e6c671103f9508816588e0fb9cec40444e8e72993f3d4c325936/beautifulsoup4-4.5.3.tar.gz",
    ],
)

bind(
    name = "beautifulsoup4",
    actual = "@beautifulsoup4_archive//:beautifulsoup4",
)

new_http_archive(
    name = "webtest_archive",
    build_file = "//third_party:webtest.BUILD",
    sha256 = "2b6abd2689f28a0b3575bcb5a36757f2344670dd13a8d9272d3a987c2fd1b615",
    strip_prefix = "WebTest-2.0.27",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/80/fa/ca3a759985c72e3a124cbca3e1f8a2e931a07ffd31fd45d8f7bf21cb95cf/WebTest-2.0.27.tar.gz",
        "https://pypi.python.org/packages/80/fa/ca3a759985c72e3a124cbca3e1f8a2e931a07ffd31fd45d8f7bf21cb95cf/WebTest-2.0.27.tar.gz",
    ],
)

bind(
    name = "webtest",
    actual = "@webtest_archive//:webtest",
)

git_repository(
    name = "absl_git",
    remote = "https://github.com/abseil/abseil-py.git",
    commit = "e7e488817ecce91d290d7fcce997b8dda1c6ee77",
)

new_http_archive(
    name = "keyczar_archive",
    build_file = "//third_party:keyczar.BUILD",
    sha256 = "a872cbfd3679fe847ed9f738cb8a1481fb1a4e6b829df8f396bc16519dc33e03",
    urls = ["https://github.com/google/keyczar/archive/Python_release_0.716.zip"],
    strip_prefix = "keyczar-Python_release_0.716/python/src/",
)

bind(
    name = "keyczar",
    actual = "@keyczar_archive//:keyczar",
)

# needed for oauth2client
new_http_archive(
    name = "httplib2_archieve",
    build_file = "//third_party:httplib2.BUILD",
    sha256 = "b5593c8b119cc4657d93b5a8923bc1dd43609f7afa9dac707a519d6d9ee984b3",
    urls = ["https://github.com/httplib2/httplib2/archive/v0.10.3.zip"],
    strip_prefix = "httplib2-0.10.3/python2/",
)

bind(
    name = "httplib2",
    actual = "@httplib2_archieve//:httplib2",
)

new_git_repository(
    name = "rsa_git",
    build_file = "//third_party:rsa.BUILD",
    commit = "d00852509aa3702827941882941dc1c76368cf8c",
    remote = "https://github.com/sybrenstuvel/python-rsa.git",
)

bind(
    name = "rsa",
    actual = "@rsa_git//:rsa",
)

new_git_repository(
    name = "pyasn1_git",
    build_file = "//third_party:pyasn1.BUILD",
    commit = "24d5afade36b05d7ba79460b8a9d4e5d99e19918",
    remote = "https://github.com/etingof/pyasn1.git",
)

bind(
    name = "pyasn1",
    actual = "@pyasn1_git//:pyasn1",
)

new_git_repository(
    name = "oauth2client_git",
    build_file = "//third_party:oauth2client.BUILD",
    commit = "97320af2733f7bdbe47f067327610e348f953ae1",
    remote = "https://github.com/google/oauth2client.git",
)

bind(
    name = "oauth2client",
    actual = "@oauth2client_git//:oauth2client",
)

new_http_archive(
    name = "fancy_urllib_archive",
    build_file = "//third_party:fancy_urllib.BUILD",
    sha256 = "06e08edbfb64c52157582625010078deedcf08130f84a2c9a81193bbebdf6afa",
    strip_prefix = "google_appengine/lib/fancy_urllib",
    urls = [
        "https://storage.googleapis.com/appengine-sdks/featured/google_appengine_1.9.50.zip",
    ],
)

bind(
    name = "fancy_urllib",
    actual = "@fancy_urllib_archive//:fancy_urllib",
)

http_archive(
    name = "io_bazel_rules_closure",
    sha256 = "e9e2538b1f7f27de73fa2914b7d2cb1ce2ac01d1abe8390cfe51fb2558ef8b27",
    strip_prefix = "rules_closure-4c559574447f90751f05155faba4f3344668f666",
    urls = [
        "http://mirror.bazel.build/github.com/bazelbuild/rules_closure/archive/4c559574447f90751f05155faba4f3344668f666.tar.gz",
        "https://github.com/bazelbuild/rules_closure/archive/4c559574447f90751f05155faba4f3344668f666.tar.gz",  # 2017-06-21
    ],
)

load("@io_bazel_rules_closure//closure:defs.bzl", "closure_repositories")

load("@io_bazel_rules_closure//closure/private:java_import_external.bzl", "java_import_external")
java_import_external(
    name = "org_jsoup",
    licenses = ["notice"],  # The MIT License
    jar_urls = [
        "https://github.com/maximermilov/jsoup/releases/download/jsoup-1.11.1/jsoup-1.11.1-SNAPSHOT.jar",
    ],
    jar_sha256 = "7bd1599f61c613820591f92769b0510389e8afe087e89333f3d45f207a9f18ed",
)
closure_repositories(omit_org_jsoup=True)

load("//third_party:polymer.bzl", "polymer_workspace")
polymer_workspace()

git_repository(
    name = "org_tensorflow_tensorboard",
    commit = "e5d261a150207b72c7fd2d7a7253b75b9d50d468",
    remote = "https://github.com/tensorflow/tensorboard.git",
)

load("@io_bazel_rules_closure//closure:defs.bzl", "filegroup_external")
filegroup_external(
    name = "com_google_javascript_closure_compiler_externs",
    licenses = ["notice"],  # Apache 2.0
    sha256_urls_extract = {
        "0f515a6ebfa138490b3c5ea9f3591ea1a7e4a930d3074f18b3eca86084ad9b66": [
            "http://mirror.bazel.build/github.com/google/closure-compiler/archive/b37e6000001b0a6bf4c0be49024ebda14a8711d9.tar.gz",  # 2017-06-02
            "https://github.com/google/closure-compiler/archive/b37e6000001b0a6bf4c0be49024ebda14a8711d9.tar.gz",
        ],
    },
    strip_prefix = {"b37e6000001b0a6bf4c0be49024ebda14a8711d9.tar.gz": "closure-compiler-b37e6000001b0a6bf4c0be49024ebda14a8711d9/externs"},
)

filegroup_external(
    name = "com_google_javascript_closure_compiler_externs_polymer",
    licenses = ["notice"],  # Apache 2.0
    sha256_urls = {
        "23baad9a200a717a821c6df504c84d3a893d7ea9102b14876eb80097e3b94292": [
            "http://mirror.bazel.build/raw.githubusercontent.com/google/closure-compiler/0e8dc5597a295ee259e3fecd98d6535dc621232f/contrib/externs/polymer-1.0.js",  # 2017-05-27
            "https://raw.githubusercontent.com/google/closure-compiler/0e8dc5597a295ee259e3fecd98d6535dc621232f/contrib/externs/polymer-1.0.js",
        ],
    },
)

# needed for googleapiclient
new_http_archive(
    name = "uritemplate_archive",
    build_file = "//third_party:uritemplate.BUILD",
    sha256 = "c02643cebe23fc8adb5e6becffe201185bf06c40bda5c0b4028a93f1527d011d",
    strip_prefix = "uritemplate-3.0.0",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/cd/db/f7b98cdc3f81513fb25d3cbe2501d621882ee81150b745cdd1363278c10a/uritemplate-3.0.0.tar.gz",
        "https://pypi.python.org/packages/cd/db/f7b98cdc3f81513fb25d3cbe2501d621882ee81150b745cdd1363278c10a/uritemplate-3.0.0.tar.gz",
    ],
)

bind(
    name = "uritemplate",
    actual = "@uritemplate_archive//:uritemplate",
)

new_git_repository(
    name = "googleapiclient_git",
    build_file = "//third_party:googleapiclient.BUILD",
    remote = "https://github.com/google/google-api-python-client.git",
    tag = "v1.5.5",
)

bind(
    name = "googleapiclient",
    actual = "@googleapiclient_git//:googleapiclient",
)

git_repository(
    name = "io_bazel_rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    commit = "40d44a7258a9016925969e2ff41c93881ddd7155",
)
load("@io_bazel_rules_python//python:pip.bzl", "pip_import")

pip_import(
   name = "pip_deps",
   requirements = "//third_party:requirements.txt",
)

load("@pip_deps//:requirements.bzl", "pip_install")
pip_install()
