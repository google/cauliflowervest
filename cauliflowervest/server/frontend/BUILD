package(default_visibility = ["//cauliflowervest"])

load("//cauliflowervest:builddefs.bzl", "webcomponent_library")

webcomponent_library(
    name = "access_log",
    srcs = [
        "cv-access-log.html",
        "cv-access-log.js",
    ],
    destdir = "cv-access-log",
    deps = [
        "@org_polymer",
        "@org_polymer_iron_ajax",
        "@org_polymer_iron_icon",
        "@org_polymer_iron_icons",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_icon_button",
        "@org_polymer_paper_spinner",
    ],
)

webcomponent_library(
    name = "admin_page",
    srcs = [
        "cv-admin-page.html",
        "cv-admin-page.js",
    ],
    destdir = "cv-admin-page",
    deps = [
        "@org_polymer",
        "@org_polymer_iron_ajax",
        "@org_polymer_paper_button",
    ],
)

webcomponent_library(
    name = "logs_page",
    srcs = [
        "cv-logs-page.html",
        "cv-logs-page.js",
    ],
    destdir = "cv-logs-page",
    deps = [
        ":access_log",
        ":created_list",
        "@com_github_lazypages",
        "@org_polymer",
        "@org_polymer_iron_pages",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_tabs",
    ],
)

webcomponent_library(
    name = "cauliflowervest_app",
    srcs = [
        "cauliflowervest-app.css",
        "cauliflowervest-app.html",
        "cauliflowervest-app.js",
    ],
    destdir = "cauliflowervest-app",
    deps = [
        ":admin_page",
        ":logs_page",
        ":reveal_secret",
        ":search_page",
        "@com_github_lazypages",
        "@org_polymer",
        "@org_polymer_app_route",
        "@org_polymer_iron_flex_layout",
        "@org_polymer_iron_icons",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_dialog",
        "@org_polymer_paper_drawer_panel",
        "@org_polymer_paper_header_panel",
        "@org_polymer_paper_icon_button",
        "@org_polymer_paper_item",
        "@org_polymer_paper_menu",
        "@org_polymer_paper_spinner",
        "@org_polymer_paper_styles",
        "@org_polymer_paper_tabs",
        "@org_polymer_paper_toolbar",
    ],
)

webcomponent_library(
    name = "created_list",
    srcs = [
        "cv-created-list.html",
        "cv-created-list.js",
    ],
    destdir = "cv-created-list",
    deps = [
        "@org_polymer",
        "@org_polymer_iron_ajax",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_spinner",
    ],
)

webcomponent_library(
    name = "search_card",
    srcs = [
        "cv-search-card.html",
        "cv-search-card.js",
    ],
    destdir = "cv-search-card",
    deps = [
        "@org_polymer",
        "@org_polymer_iron_a11y_keys",
        "@org_polymer_iron_ajax",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_button",
        "@org_polymer_paper_card",
        "@org_polymer_paper_checkbox",
        "@org_polymer_paper_dropdown_menu",
        "@org_polymer_paper_input",
        "@org_polymer_paper_item",
        "@org_polymer_paper_menu",
    ],
)

webcomponent_library(
    name = "search_page",
    srcs = [
        "cv-search-page.html",
        "cv-search-page.js",
    ],
    destdir = "cv-search-page",
    deps = [
        ":search_card",
        ":search_result",
        "@org_polymer",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_button",
        "@org_polymer_paper_card",
        "@org_polymer_paper_checkbox",
        "@org_polymer_paper_dropdown_menu",
        "@org_polymer_paper_icon_button",
        "@org_polymer_paper_item",
        "@org_polymer_paper_menu",
        "@org_polymer_paper_menu_button",
        "@org_polymer_paper_spinner",
    ],
)

webcomponent_library(
    name = "search_result",
    srcs = [
        "cv-search-result.html",
        "cv-search-result.js",
    ],
    destdir = "cv-search-result",
    deps = [
        ":change_owner",
        ":reveal_secret",
        "@org_polymer",
        "@org_polymer_iron_ajax",
        "@org_polymer_iron_icon",
        "@org_polymer_iron_icons",
        "@org_polymer_iron_localstorage",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_button",
        "@org_polymer_paper_checkbox",
        "@org_polymer_paper_dialog",
        "@org_polymer_paper_spinner",
    ],
)

webcomponent_library(
    name = "reveal_secret",
    srcs = [
        "cv-reveal-secret.html",
        "cv-reveal-secret.js",
    ],
    destdir = "cv-reveal-secret",
    deps = [
        "@org_polymer",
        "@org_polymer_iron_ajax",
        "@org_polymer_iron_pages",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_icon_button",
        "@org_polymer_paper_spinner",
        "@org_polymer_paper_tabs",
        "@org_polymer_paper_tooltip",
    ],
)

webcomponent_library(
    name = "change_owner",
    srcs = [
        "cv-change-owner-dialog.html",
        "cv-change-owner-dialog.js",
    ],
    destdir = "cv-change-owner-dialog",
    deps = [
        "@org_polymer",
        "@org_polymer_iron_ajax",
        "@org_polymer_iron_form",
        "@org_polymer_iron_signals",
        "@org_polymer_paper_button",
        "@org_polymer_paper_dialog",
        "@org_polymer_paper_input",
        "@org_polymer_paper_spinner",
    ],
)
