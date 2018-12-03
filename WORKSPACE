load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository", "new_git_repository")

http_archive(
    name = "subpar",
    sha256 = "3e300d4326dc3661fd36b473cc42f5a6b0c856edb36f4cce33514d5b4d37f6f3",
    strip_prefix = "subpar-1.0.0",
    urls = ["https://github.com/google/subpar/archive/1.0.0.tar.gz"],
)

git_repository(
    name = "io_bazel_rules_appengine",
    commit = "17c3c8471477a9ec7f993d35a54bfb26798b05c5",
    remote = "https://github.com/bazelbuild/rules_appengine.git",
)

load("@io_bazel_rules_appengine//appengine:py_appengine.bzl", "py_appengine_repositories")
load("@io_bazel_rules_appengine//appengine:sdk.bzl", "appengine_repositories")

appengine_repositories()
py_appengine_repositories()

# needed for mock, webtest
http_archive(
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

http_archive(
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
http_archive(
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
http_archive(
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

http_archive(
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

http_archive(
    name = "absl_git",
    sha256 = "980ce58c34dfa75a9d20d45c355658191c166557f1de41ab52f208bd00604c2b",
    strip_prefix = "abseil-py-b347ba6022370f895d3133241ed96965b95ecb40",
    urls = ["https://github.com/abseil/abseil-py/archive/b347ba6022370f895d3133241ed96965b95ecb40.tar.gz"],
)

http_archive(
    name = "keyczar_archive",
    build_file = "//third_party:keyczar.BUILD",
    sha256 = "a872cbfd3679fe847ed9f738cb8a1481fb1a4e6b829df8f396bc16519dc33e03",
    strip_prefix = "keyczar-Python_release_0.716/python/src/",
    urls = ["https://github.com/google/keyczar/archive/Python_release_0.716.zip"],
)

bind(
    name = "keyczar",
    actual = "@keyczar_archive//:keyczar",
)

# needed for oauth2client
http_archive(
    name = "httplib2_archive",
    build_file = "//third_party:httplib2.BUILD",
    sha256 = "b5593c8b119cc4657d93b5a8923bc1dd43609f7afa9dac707a519d6d9ee984b3",
    strip_prefix = "httplib2-0.10.3/python2/",
    urls = ["https://github.com/httplib2/httplib2/archive/v0.10.3.zip"],
)

bind(
    name = "httplib2",
    actual = "@httplib2_archive//:httplib2",
)

http_archive(
    name = "rsa_archive",
    build_file = "//third_party:rsa.BUILD",
    sha256 = "a25e4847ee24ec94af94ecd6a721f869be1136ffbc7df885dfd851dd6c948269",
    strip_prefix = "python-rsa-version-3.4.2",
    urls = ["https://github.com/sybrenstuvel/python-rsa/archive/version-3.4.2.tar.gz"],
)

bind(
    name = "rsa",
    actual = "@rsa_archive//:rsa",
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

http_archive(
    name = "oauth2client_archive",
    build_file = "//third_party:oauth2client.BUILD",
    sha256 = "77737f8f831a1306b022deb2cf6f3c9dbe4b338b8b9afcf84e7be5bef4d7e833",
    strip_prefix = "oauth2client-4.1.2",
    urls = ["https://github.com/google/oauth2client/archive/v4.1.2.tar.gz"],
)

bind(
    name = "oauth2client",
    actual = "@oauth2client_archive//:oauth2client",
)

http_archive(
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
    sha256 = "e3a384a34ab7f54f3b2e65d6c9b015aed665bab3ee265396f3876f0c53729525",
    strip_prefix = "rules_closure-7448ab3b1f53db99419a2b1a1b84f9ba2d79ec03",
    urls = [
        "https://github.com/bazelbuild/rules_closure/archive/7448ab3b1f53db99419a2b1a1b84f9ba2d79ec03.tar.gz",  # 2018-11-15
    ],
)

load("@io_bazel_rules_closure//closure:defs.bzl", "closure_repositories")
load("@io_bazel_rules_closure//closure/private:java_import_external.bzl", "java_import_external")

java_import_external(
    name = "org_jsoup",
    jar_sha256 = "7bd1599f61c613820591f92769b0510389e8afe087e89333f3d45f207a9f18ed",
    jar_urls = [
        "https://github.com/maximermilov/jsoup/releases/download/jsoup-1.11.1/jsoup-1.11.1-SNAPSHOT.jar",
    ],
    licenses = ["notice"],  # The MIT License
)

closure_repositories(omit_org_jsoup = True)

load("//third_party:polymer.bzl", "polymer_workspace")

polymer_workspace()

http_archive(
    name = "org_tensorflow_tensorboard",
    sha256 = "7e59a8047a92868d0c85a83062969624c97522357e62706b2fcd17a0121d5d1c",
    strip_prefix = "tensorboard-4ee5780cf89389152e61488f7ce843a2b343f5e6",
    urls = ["https://github.com/tensorflow/tensorboard/archive/4ee5780cf89389152e61488f7ce843a2b343f5e6.zip"],
)
load("@org_tensorflow_tensorboard//third_party:fonts.bzl", "tensorboard_fonts_workspace")
tensorboard_fonts_workspace()

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
http_archive(
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

http_archive(
    name = "googleapiclient_archive",
    build_file = "//third_party:googleapiclient.BUILD",
    sha256 = "4a807d2c6ea83186f0cb6ede00f42e0f4cf6daf01c4ec1e7e24863113527204d",
    strip_prefix = "google-api-python-client-1.6.4",
    urls = ["https://github.com/google/google-api-python-client/archive/v1.6.4.tar.gz"],
)

bind(
    name = "googleapiclient",
    actual = "@googleapiclient_archive//:googleapiclient",
)

git_repository(
    name = "io_bazel_rules_python",
    commit = "b25495c47eb7446729a2ed6b1643f573afa47d99",
    remote = "https://github.com/bazelbuild/rules_python.git",
)

load("@io_bazel_rules_python//python:pip.bzl", "pip_import")

pip_import(
    name = "pip_deps",
    requirements = "//third_party:requirements.txt",
)

load("@pip_deps//:requirements.bzl", "pip_install")

pip_install()

load("@io_bazel_rules_closure//closure:defs.bzl", "web_library_external")
web_library_external(
  name = "com_github_lazypages",
  licenses = ["notice"],  # BSD 3-Clause
  sha256 = "d9adb38000d65297c83b856157c2b62b70c0e322db13c83a55543e526d502ed7",
  urls = [
    "https://github.com/maximermilov/lazy-pages/archive/32e17afa4386d55f182a38d9338c8ec2d4bf4d9d.tar.gz",
  ],
  strip_prefix = "lazy-pages-32e17afa4386d55f182a38d9338c8ec2d4bf4d9d",
  path = "/lazy-pages",
  srcs = [
    "lazy-pages.html",
  ],
  deps = [
    "@org_polymer",
    "@org_polymer_neon_animation",
    "@org_polymer_iron_resizable_behavior",
  ],
)
