package(default_visibility = ["//cauliflowervest"])

load(
    "//cauliflowervest:builddefs.bzl",
    "cv_appengine_test",
)

# Libraries.
py_library(
    name = "all",
    deps = [
        ":apple_firmware",
        ":bitlocker",
        ":created",
        ":duplicity",
        ":filevault",
        ":linux_firmware",
        ":logs",
        ":luks",
        ":maintenance",
        ":provisioning",
        ":rekey",
        ":retired_assets",
        ":search",
        ":volume_types",
        ":windows_firmware",
        ":xsrf",
    ],
)

py_library(
    name = "base_handler",
    srcs = ["base_handler.py"],
    deps = [
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:settings",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "retired_assets",
    srcs = ["retired_assets.py"],
    deps = [
        ":base_handler",
        "//cauliflowervest/server:service_factory",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "passphrase_handler",
    srcs = ["passphrase_handler.py"],
    deps = [
        ":base_handler",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:service_factory",
        "//cauliflowervest/server:settings",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "bitlocker",
    srcs = ["bitlocker.py"],
    deps = [
        ":passphrase_handler",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "change_owner_handler",
    srcs = ["change_owner_handler.py"],
    deps = [
        "//cauliflowervest:settings",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server/handlers:base_handler",
        "//cauliflowervest/server/models:base",
    ],
)

py_library(
    name = "duplicity",
    srcs = ["duplicity.py"],
    deps = [
        ":passphrase_handler",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "filevault",
    srcs = ["filevault.py"],
    deps = [
        ":change_owner_handler",
        ":passphrase_handler",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server/models:volumes",
    ],
)

py_library(
    name = "logs",
    srcs = ["logs.py"],
    deps = [
        ":passphrase_handler",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "luks",
    srcs = ["luks.py"],
    deps = [
        ":passphrase_handler",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "firmware_handler",
    srcs = ["firmware_handler.py"],
    deps = [
        ":passphrase_handler",
        "//cauliflowervest:settings",
        "//cauliflowervest/server:service_factory",
        "//cauliflowervest/server/handlers:base_handler",
        "//cauliflowervest/server/models:base",
    ],
)

py_library(
    name = "apple_firmware",
    srcs = ["apple_firmware.py"],
    deps = [
        ":change_owner_handler",
        ":firmware_handler",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server/models:firmware",
    ],
)

py_library(
    name = "linux_firmware",
    srcs = ["linux_firmware.py"],
    deps = [
        ":change_owner_handler",
        ":firmware_handler",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server/models:firmware",
    ],
)

py_library(
    name = "windows_firmware",
    srcs = ["windows_firmware.py"],
    deps = [
        ":firmware_handler",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server/models:firmware",
    ],
)

py_library(
    name = "search",
    srcs = ["search.py"],
    deps = [
        ":base_handler",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "created",
    srcs = ["created.py"],
    deps = [
        ":base_handler",
        "//cauliflowervest:settings",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:settings",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "provisioning",
    srcs = ["provisioning.py"],
    deps = [
        ":base_handler",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "xsrf",
    srcs = ["xsrf.py"],
    deps = [
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "volume_types",
    srcs = ["volume_types.py"],
    deps = [
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "maintenance",
    srcs = ["maintenance.py"],
    deps = [
        "//cauliflowervest/server/models",
    ],
)

py_library(
    name = "rekey",
    srcs = ["rekey.py"],
    deps = [
        "//cauliflowervest/server/models",
    ],
)

# Tests
py_library(
    name = "test_util",
    testonly = 1,
    srcs = ["test_util.py"],
    deps = [
        "//cauliflowervest/server:crypto",
        "//cauliflowervest/server/models",
        "//common/testing:basetest",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "apple_firmware_test",
    srcs = [
        "apple_firmware_test.py",
    ],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":apple_firmware",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "linux_firmware_test",
    srcs = [
        "linux_firmware_test.py",
    ],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":linux_firmware",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "windows_firmware_test",
    srcs = [
        "windows_firmware_test.py",
    ],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":test_util",
        ":windows_firmware",
        "//cauliflowervest/server:main_lib",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "duplicity_test",
    size = "small",
    srcs = [
        "duplicity_test.py",
    ],
    deps = [
        ":duplicity",
        ":test_util",
        "//cauliflowervest/server:util",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "filevault_test",
    size = "small",
    srcs = [
        "filevault_test.py",
    ],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":filevault",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "provisioning_test",
    size = "small",
    srcs = [
        "provisioning_test.py",
    ],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":provisioning",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "passphrase_handler_test",
    size = "small",
    srcs = ["passphrase_handler_test.py"],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":passphrase_handler",
        ":test_util",
        "//cauliflowervest/server:crypto",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:settings",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
        "@absl_git//absl/testing:parameterized",
    ],
)

cv_appengine_test(
    name = "luks_test",
    size = "small",
    srcs = [
        "luks_test.py",
    ],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":luks",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:settings",
        "//cauliflowervest/server:util",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "search_test",
    size = "small",
    srcs = [
        "search_test.py",
    ],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":search",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "volume_types_test",
    size = "small",
    srcs = [
        "volume_types_test.py",
    ],
    deps = [
        ":test_util",
        ":volume_types",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "created_test",
    size = "small",
    srcs = [
        "created_test.py",
    ],
    data = [
        "//cauliflowervest/server/templates",
    ],
    deps = [
        ":created",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "maintenance_test",
    size = "small",
    srcs = [
        "maintenance_test.py",
    ],
    deps = [
        ":maintenance",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server:permissions",
        "//cauliflowervest/server:util",
        "//cauliflowervest/server/models",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "xsrf_test",
    size = "small",
    srcs = [
        "xsrf_test.py",
    ],
    deps = [
        ":test_util",
        ":xsrf",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server/models",
        "//external:mock",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "retired_assets_test",
    size = "small",
    srcs = [
        "retired_assets_test.py",
    ],
    deps = [
        ":retired_assets",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//external:mock",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "logs_test",
    size = "small",
    srcs = [
        "logs_test.py",
    ],
    deps = [
        ":logs",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server/models",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

cv_appengine_test(
    name = "rekey_test",
    srcs = [
        "rekey_test.py",
    ],
    deps = [
        ":rekey",
        ":test_util",
        "//cauliflowervest/server:main_lib",
        "//cauliflowervest/server/models",
        "//external:webtest",
        "@absl_git//absl/testing:absltest",
    ],
)

test_suite(
    name = "smoke_tests",
    tests = [
        ":apple_firmware_test",
        ":created_test",
        ":duplicity_test",
        ":filevault_test",
        ":linux_firmware_test",
        ":logs_test",
        ":luks_test",
        ":maintenance_test",
        ":passphrase_handler_test",
        ":provisioning_test",
        ":rekey_test",
        ":search_test",
        ":volume_types_test",
        ":windows_firmware_test",
        ":xsrf_test",
    ],
)
