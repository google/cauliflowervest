load("@io_bazel_rules_closure//closure:defs.bzl", "web_library_external")

def polymer_workspace():
    web_library_external(
        name = "org_polymer",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "af1ad81af6ce0a146c45f47775f11201f45af25930ed5b153b8a9de72bec00f2",
        strip_prefix = "polymer-2.2.0",
        urls = [
            "https://github.com/Polymer/polymer/archive/v2.2.0.tar.gz",
        ],
        path = "/polymer",
        srcs = [
            "lib/mixins/element-mixin.html",
            "lib/mixins/dir-mixin.html",
            "lib/mixins/property-effects.html",
            "lib/mixins/gesture-event-listeners.html",
            "lib/mixins/mutable-data.html",
            "lib/mixins/property-accessors.html",
            "lib/mixins/template-stamp.html",
            "lib/elements/array-selector.html",
            "lib/elements/custom-style.html",
            "lib/elements/dom-if.html",
            "lib/elements/dom-repeat.html",
            "lib/elements/dom-bind.html",
            "lib/elements/dom-module.html",
            "lib/legacy/legacy-element-mixin.html",
            "lib/legacy/polymer-fn.html",
            "lib/legacy/polymer.dom.html",
            "lib/legacy/mutable-data-behavior.html",
            "lib/legacy/class.html",
            "lib/legacy/templatizer-behavior.html",
            "lib/utils/path.html",
            "lib/utils/flush.html",
            "lib/utils/mixin.html",
            "lib/utils/async.html",
            "lib/utils/import-href.html",
            "lib/utils/render-status.html",
            "lib/utils/settings.html",
            "lib/utils/case-map.html",
            "lib/utils/flattened-nodes-observer.html",
            "lib/utils/boot.html",
            "lib/utils/gestures.html",
            "lib/utils/debounce.html",
            "lib/utils/templatize.html",
            "lib/utils/array-splice.html",
            "lib/utils/style-gather.html",
            "lib/utils/unresolved.html",
            "lib/utils/resolve-url.html",
            "polymer-element.html",
            "polymer.html",
        ],
        deps = [
            "@org_webcomponents_shadycss",
        ],
    )
    web_library_external(
        name = "org_webcomponents_shadycss",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "d9fd7dfbacbfe0d0b53337e7def694adc59f1a1dd3c63290d0fbdbb8de0efc69",
        strip_prefix = "shadycss-1.1.0",
        urls = [
            "https://github.com/webcomponents/shadycss/archive/v1.1.0.tar.gz",
        ],
        path = "/shadycss",
        srcs = [
            "custom-style-interface.html",
            "apply-shim.html",
            "apply-shim.min.js",
            "custom-style-interface.min.js",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_ajax",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "",
        strip_prefix = "iron-ajax-2.0.6",
        urls = [
            "https://github.com/PolymerElements/iron-ajax/archive/v2.0.6.tar.gz",
        ],
        path = "/iron-ajax",
        srcs = [
            "iron-request.html",
            "iron-ajax.html",
        ],
        deps = [
            "@org_polymer",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_card",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "7cad4022654485f45a71e815db194818690f6375da34acb6ed4403b0da0ebd35",
        urls = [
            "https://github.com/PolymerElements/paper-card/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-card-2.1.0",
        path = "/paper-card",
        srcs = ["paper-card.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_iron_image",
            "@org_polymer_paper_styles",
            "@org_polymer_paper_material",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_styles",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "37359c72f96f1f3dd90fe7a9ba50d079dc32241de359d5c19c013b564b48bd3f",
        urls = [
            "https://github.com/PolymerElements/paper-styles/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-styles-2.1.0",
        path = "/paper-styles",
        srcs = [
            "element-styles/paper-material-styles.html",
            "element-styles/paper-item-styles.html",
            "classes/global.html",
            "classes/shadow.html",
            "classes/typography.html",
            "color.html",
            "default-theme.html",
            "demo-pages.html",
            "paper-styles.html",
            "paper-styles-classes.html",
            "shadow.html",
            "typography.html",
        ],
        deps = [
            "@org_polymer",
            "@com_google_fonts_roboto",
            "@org_polymer_iron_flex_layout",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_flex_layout",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "2c147ed1e99870f44aa6e36ff718eee056e49417f64d0ca25caaed781d479ffc",
        urls = [
            "https://github.com/PolymerElements/iron-flex-layout/archive/v2.0.3.tar.gz",
        ],
        strip_prefix = "iron-flex-layout-2.0.3",
        path = "/iron-flex-layout",
        srcs = [
            "iron-flex-layout.html",
            "iron-flex-layout-classes.html",
        ],
        deps = ["@org_polymer"],
    )
    web_library_external(
        name = "org_polymer_paper_material",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "913e9c63cf5c8286b0fab817079d7dc900a343d2c05809995d8d9ba0e41f8a29",
        urls = [
            "https://mirror.bazel.build/github.com/PolymerElements/paper-material/archive/v2.0.0.tar.gz",
            "https://github.com/PolymerElements/paper-material/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "paper-material-2.0.0",
        path = "/paper-material",
        srcs = [
            "paper-material.html",
            "paper-material-shared-styles.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_image",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "4a971e877316e0b81bc15be102c14c5b938035443d6d2e43e9d96be6e8ba8bfa",
        urls = [
            "https://github.com/PolymerElements/iron-image/archive/v2.2.0.tar.gz",
        ],
        strip_prefix = "iron-image-2.2.0",
        path = "/iron-image",
        srcs = ["iron-image.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_flex_layout",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_spinner",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "df74ce25bdf16df7f82d4567b0a353073de811f6d3d38df95477b7cefa773688",
        urls = [
            "https://github.com/PolymerElements/paper-spinner/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-spinner-2.1.0",
        path = "/paper-spinner",
        srcs = [
            "paper-spinner.html",
            "paper-spinner-behavior.html",
            "paper-spinner-lite.html",
            "paper-spinner-styles.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_dialog",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "cf60d3aa6ad57ba4eb8b1c16713e65057735eed94b009aeebdbcf3436c95a161",
        urls = [
            "https://github.com/PolymerElements/paper-dialog/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "paper-dialog-2.0.0",
        path = "/paper-dialog",
        srcs = [
            "paper-dialog.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_neon_animation",
            "@org_polymer_paper_dialog_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_a11y_keys_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "09274155c8d537f8bb567b3be5e747253ef760995a59ee06cb0ab38e704212fb",
        urls = [
            "https://mirror.bazel.build/github.com/PolymerElements/iron-a11y-keys-behavior/archive/v2.0.0.tar.gz",
            "https://github.com/PolymerElements/iron-a11y-keys-behavior/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "iron-a11y-keys-behavior-2.0.0",
        path = "/iron-a11y-keys-behavior",
        srcs = ["iron-a11y-keys-behavior.html"],
        deps = ["@org_polymer"],
    )
    web_library_external(
        name = "org_polymer_iron_fit_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "e0f6ee291103b64ca19e75e42afb0d4dcce87b60b5033a522cd9d2c0260486a7",
        urls = [
            "https://github.com/PolymerElements/iron-fit-behavior/archive/v2.1.1.tar.gz",
        ],
        strip_prefix = "iron-fit-behavior-2.1.1",
        path = "/iron-fit-behavior",
        srcs = ["iron-fit-behavior.html"],
        deps = ["@org_polymer"],
    )
    web_library_external(
        name = "org_polymer_iron_meta",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "65366ae55474fd058e052aac01f379a5ca3fd8219e0f51cb9e379e2766d607d7",
        urls = [
            "https://github.com/PolymerElements/iron-meta/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "iron-meta-2.1.0",
        path = "/iron-meta",
        srcs = ["iron-meta.html"],
        deps = ["@org_polymer"],
    )
    web_library_external(
        name = "org_polymer_iron_selector",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "dcd7e180f05c9b66c30eedaee030a30e2f87d997f0de132e08ea4a58d494b01b",
        urls = [
            "https://github.com/PolymerElements/iron-selector/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "iron-selector-2.1.0",
        path = "/iron-selector",
        srcs = [
            "iron-multi-selectable.html",
            "iron-selectable.html",
            "iron-selection.html",
            "iron-selector.html",
        ],
        deps = ["@org_polymer"],
    )

    web_library_external(
        name = "org_polymer_iron_overlay_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "1f678414a71ab0fe6ed4b8df1f47ed820191073063d3abe8a61d05dff266078f",
        urls = [
            "https://github.com/PolymerElements/iron-overlay-behavior/archive/v2.3.3.tar.gz",
        ],
        strip_prefix = "iron-overlay-behavior-2.3.3",
        path = "/iron-overlay-behavior",
        srcs = [
            "iron-focusables-helper.html",
            "iron-overlay-backdrop.html",
            "iron-overlay-behavior.html",
            "iron-overlay-manager.html",
            "iron-scroll-manager.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
            "@org_polymer_iron_fit_behavior",
            "@org_polymer_iron_resizable_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_web_animations_js",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "f8bd760cbdeba131f6790bd5abe170bcbf7b1755ff58ed16d0b82fa8a7f34a7f",
        urls = [
            "https://mirror.bazel.build/github.com/web-animations/web-animations-js/archive/2.2.1.tar.gz",
            "https://github.com/web-animations/web-animations-js/archive/2.2.1.tar.gz",
        ],
        strip_prefix = "web-animations-js-2.2.1",
        path = "/web-animations-js",
        srcs = ["web-animations-next-lite.min.js"],
    )
    web_library_external(
        name = "org_polymer_iron_resizable_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "1bd7875d419a63f3c8d4ca3309b53ecf93d8dddb9703913f5442d04903a89976",
        urls = [
            "https://github.com/PolymerElements/iron-resizable-behavior/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "iron-resizable-behavior-2.1.0",
        path = "/iron-resizable-behavior",
        srcs = ["iron-resizable-behavior.html"],
        deps = ["@org_polymer"],
    )
    web_library_external(
        name = "org_polymer_neon_animation",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "03f827505a229bf03006b8d804f403df070cd3c4ca89521091be156eaf50f786",
        urls = [
            "https://github.com/PolymerElements/neon-animation/archive/v2.2.0.tar.gz",
        ],
        strip_prefix = "neon-animation-2.2.0",
        path = "/neon-animation",
        srcs = [
            "animations/cascaded-animation.html",
            "animations/fade-in-animation.html",
            "animations/fade-out-animation.html",
            "animations/hero-animation.html",
            "animations/opaque-animation.html",
            "animations/reverse-ripple-animation.html",
            "animations/ripple-animation.html",
            "animations/scale-down-animation.html",
            "animations/scale-up-animation.html",
            "animations/slide-down-animation.html",
            "animations/slide-from-bottom-animation.html",
            "animations/slide-from-left-animation.html",
            "animations/slide-from-right-animation.html",
            "animations/slide-from-top-animation.html",
            "animations/slide-left-animation.html",
            "animations/slide-right-animation.html",
            "animations/slide-up-animation.html",
            "animations/transform-animation.html",
            "neon-animatable.html",
            "neon-animatable-behavior.html",
            "neon-animated-pages.html",
            "neon-animation.html",
            "neon-animation-behavior.html",
            "neon-animation-runner-behavior.html",
            "neon-animations.html",
            "neon-shared-element-animatable-behavior.html",
            "neon-shared-element-animation-behavior.html",
            "web-animations.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_meta",
            "@org_polymer_iron_resizable_behavior",
            "@org_polymer_iron_selector",
            "@org_polymer_web_animations_js",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_dialog_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "5b03e3c830e73e6fff6247fa04b1cc546991e348eb7cb575052aaa95f050d145",
        urls = [
            "https://github.com/PolymerElements/paper-dialog-behavior/archive/v2.2.0.tar.gz",
        ],
        strip_prefix = "paper-dialog-behavior-2.2.0",
        path = "/paper-dialog-behavior",
        srcs = [
            "paper-dialog-behavior.html",
            "paper-dialog-shared-styles.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_iron_overlay_behavior",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_behaviors",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "74090426df1f50d1071095591cf35deb5d645b9116299b2d8e9d538490bd7f32",
        urls = [
            "https://github.com/PolymerElements/paper-behaviors/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-behaviors-2.1.0",
        path = "/paper-behaviors",
        srcs = [
            "paper-ripple-behavior.html",
            "paper-inky-focus-behavior.html",
            "paper-checked-element-behavior.html",
            "paper-button-behavior.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_behaviors",
            "@org_polymer_iron_checked_element_behavior",
            "@org_polymer_paper_ripple",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_checked_element_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "3037ede91593eb2880cf2e0c8d0198ae0b5802221e7386578263ab831a058bfc",
        urls = [
            "https://github.com/PolymerElements/iron-checked-element-behavior/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "iron-checked-element-behavior-2.1.0",
        path = "/iron-checked-element-behavior",
        srcs = ["iron-checked-element-behavior.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_form_element_behavior",
            "@org_polymer_iron_validatable_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_form_element_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "c4541ac5f6c8f2677ab05fde9c5d911af58070e1b97f9d603fe489c40a10c1f0",
        urls = [
            "https://github.com/PolymerElements/iron-form-element-behavior/archive/v2.1.1.tar.gz",
        ],
        strip_prefix = "iron-form-element-behavior-2.1.1",
        path = "/iron-form-element-behavior",
        srcs = ["iron-form-element-behavior.html"],
        deps = ["@org_polymer"],
    )
    web_library_external(
        name = "org_polymer_iron_validatable_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "3d60d1770c9ea57ba9dff8a43f7c07f258c5c233e2b1b307b5ef6ed31573d45d",
        urls = [
            "https://github.com/PolymerElements/iron-validatable-behavior/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "iron-validatable-behavior-2.1.0",
        path = "/iron-validatable-behavior",
        srcs = ["iron-validatable-behavior.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_meta",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_behaviors",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "71ecbe6a01bc302cdea01c80bf7b5801e1f570c88cc4ac491591e5cf19fdedfe",
        urls = [
            "https://github.com/PolymerElements/iron-behaviors/archive/v2.1.1.tar.gz",
        ],
        strip_prefix = "iron-behaviors-2.1.1",
        path = "/iron-behaviors",
        srcs = [
            "iron-button-state.html",
            "iron-control-state.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_iconset_svg",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "75cfb41e78f86ef6cb5d201ad12021785ef9e192b490ad46dcc15a9c19bdf71a",
        urls = [
            "https://mirror.bazel.build/github.com/PolymerElements/iron-iconset-svg/archive/v2.0.0.tar.gz",
            "https://github.com/PolymerElements/iron-iconset-svg/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "iron-iconset-svg-2.0.0",
        path = "/iron-iconset-svg",
        srcs = ["iron-iconset-svg.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_meta",
        ],
    )

    web_library_external(
        name = "org_polymer_iron_icons",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "779174b4acd9ac8fbbb3e1bf81394db13189f294bd6683c4a0e79f68da8f1911",
        urls = [
            "https://github.com/PolymerElements/iron-icons/archive/v2.1.1.tar.gz",
        ],
        strip_prefix = "iron-icons-2.1.1",
        path = "/iron-icons",
        srcs = [
            "av-icons.html",
            "communication-icons.html",
            "device-icons.html",
            "editor-icons.html",
            "hardware-icons.html",
            "image-icons.html",
            "iron-icons.html",
            "maps-icons.html",
            "notification-icons.html",
            "places-icons.html",
            "social-icons.html",
        ],
        deps = [
            "@org_polymer_iron_icon",
            "@org_polymer_iron_iconset_svg",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_ripple",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "e7a032f1c194e6222b3b4c80e04f28a201c5d12c7e94a33b77f10ab371a19d84",
        urls = [
            "https://github.com/PolymerElements/paper-ripple/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-ripple-2.1.0",
        path = "/paper-ripple",
        srcs = [
            "paper-ripple.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_icon",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "5030eb65f935ee75bec682e71c6b55a421ff365f9f876f0e920080625fc63694",
        urls = [
            "https://github.com/PolymerElements/iron-icon/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "iron-icon-2.1.0",
        path = "/iron-icon",
        srcs = [
            "iron-icon.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_meta",
            "@org_polymer_iron_flex_layout",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_icon_button",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "3026c61abdfaf9621070c879b9a6dbbdd0236d4453467b54f5672e1c22af4c27",
        urls = [
            "https://github.com/PolymerElements/paper-icon-button/archive/v2.2.0.tar.gz",
        ],
        strip_prefix = "paper-icon-button-2.2.0",
        path = "/paper-icon-button",
        srcs = [
            "paper-icon-button.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_paper_behaviors",
            "@org_polymer_iron_icon",
            "@org_polymer_iron_overlay_behavior",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_collapse",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "eb72f459a2a5adbcd922327eea02ed909e8056ad72fd8a32d04a14ce54b2e480",
        urls = [
            "http://mirror.bazel.build/github.com/PolymerElements/iron-collapse/archive/v2.0.0.tar.gz",
            "https://github.com/PolymerElements/iron-collapse/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "iron-collapse-2.0.0",
        path = "/iron-collapse",
        srcs = ["iron-collapse.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_resizable_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_menu_behavior",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "35d33d1ae55c6efaa0c3744ebe8a06cc0a8b2af9286dd8d36e20726a8540a11a",
        urls = [
            "http://mirror.bazel.build/github.com/PolymerElements/iron-menu-behavior/archive/v2.0.0.tar.gz",
            "https://github.com/PolymerElements/iron-menu-behavior/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "iron-menu-behavior-2.0.0",
        path = "/iron-menu-behavior",
        srcs = [
            "iron-menu-behavior.html",
            "iron-menubar-behavior.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
            "@org_polymer_iron_selector",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_checkbox",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "0a291d0c64de1b6b807d66697bead9c66c0d7bc3c68b8037e6667f3d66a5904c",
        urls = [
            "http://mirror.bazel.build/github.com/PolymerElements/paper-checkbox/archive/v2.0.0.tar.gz",
            "https://github.com/PolymerElements/paper-checkbox/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "paper-checkbox-2.0.0",
        path = "/paper-checkbox",
        srcs = ["paper-checkbox.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_paper_behaviors",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_listbox",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "674992d882b18a0618fa697180f196dbc052fb2f5d9ce4e19026a918b568ffd6",
        urls = [
            "http://mirror.bazel.build/github.com/PolymerElements/paper-listbox/archive/v2.0.0.tar.gz",
            "https://github.com/PolymerElements/paper-listbox/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "paper-listbox-2.0.0",
        path = "/paper-listbox",
        srcs = ["paper-listbox.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_menu_behavior",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_webcomponentsjs",
        licenses = ["notice"],  # BSD-3-Clause
        sha256 = "0513a8cffe3799f84edff7f29a0d7a3cc0a9532c7b2757e24f2d82bb26f86722",
        urls = [
            "https://github.com/webcomponents/webcomponentsjs/archive/v1.1.0.tar.gz",
        ],
        strip_prefix = "webcomponentsjs-1.1.0",
        path = "/webcomponentsjs",
        srcs = [
            "custom-elements-es5-adapter.js",
            "webcomponents-lite.js",
        ],
    )
    web_library_external(
        name = "org_polymer_app_route",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "251c84d4d8c8498886d7005928e8af8583092e34487d6c4c2b646ec493b23dae",
        urls = [
            "https://github.com/PolymerElements/app-route/archive/v2.0.2.tar.gz",
        ],
        strip_prefix = "app-route-2.0.2",
        path = "/app-route",
        srcs = [
            "app-route-converter.html",
            "app-route-converter-behavior.html",
            "app-location.html",
            "app-route.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_location",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_drawer_panel",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "94a8b85ad4b89547441eb58fcf095c31f8f95076ee62bb411b92310950082f68",
        urls = [
            "https://github.com/PolymerElements/paper-drawer-panel/archive/v2.1.1.tar.gz",
        ],
        strip_prefix = "paper-drawer-panel-2.1.1",
        path = "/paper-drawer-panel",
        srcs = [
            "paper-drawer-panel.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_selector",
            "@org_polymer_iron_resizable_behavior",
            "@org_polymer_iron_media_query",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_item",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "710dc8ae3d3aad12513de4d111aab3b0bcb31159d9fb73c9ef6d02642df4bce2",
        urls = [
            "https://github.com/PolymerElements/paper-item/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-item-2.1.0",
        path = "/paper-item",
        srcs = [
            "paper-icon-item.html",
            "paper-item.html",
            "paper-item-behavior.html",
            "paper-item-body.html",
            "paper-item-shared-styles.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_behaviors",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_pages",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "2db73155902d0f24e3ba19ef680ca620c22ebef204e9dacab470aa25677cbc7d",
        urls = [
            "https://github.com/PolymerElements/iron-pages/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "iron-pages-2.1.0",
        path = "/iron-pages",
        srcs = [
            "iron-pages.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_selector",
            "@org_polymer_iron_resizable_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_tabs",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "c09fcd78d1e1c79451c6c12c203ec32c6b36f063f25ad6cdf18da81e33bd9a2d",
        urls = [
            "https://github.com/PolymerElements/paper-tabs/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-tabs-2.1.0",
        path = "/paper-tabs",
        srcs = [
            "paper-tab.html",
            "paper-tabs.html",
            "paper-tabs-icons.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_behaviors",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_iron_icon",
            "@org_polymer_iron_iconset_svg",
            "@org_polymer_iron_menu_behavior",
            "@org_polymer_iron_resizable_behavior",
            "@org_polymer_paper_behaviors",
            "@org_polymer_paper_icon_button",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_tooltip",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "07eacd783507d4aad3e5e6e0c128c3816aa7e3149bf8f7dfce525ea5568d0565",
        urls = [
            "https://github.com/PolymerElements/paper-tooltip/archive/v2.1.1.tar.gz",
        ],
        strip_prefix = "paper-tooltip-2.1.1",
        path = "/paper-tooltip",
        srcs = ["paper-tooltip.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_neon_animation",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_menu_button",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "39ea4811c344d111d82e5150bc3441918989bcd251e5dbcd8771356a95151714",
        urls = [
            "https://github.com/PolymerElements/paper-menu-button/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-menu-button-2.1.0",
        path = "/paper-menu-button",
        srcs = [
            "paper-menu-button.html",
            "paper-menu-button-animations.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
            "@org_polymer_iron_behaviors",
            "@org_polymer_iron_dropdown",
            "@org_polymer_neon_animation",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_form",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "a2c77bd816d6f0e8d022c22739e785ec3e958ef2fd36e49ab04a0b0476a2c612",
        urls = [
            "https://github.com/PolymerElements/iron-form/archive/v2.1.3.tar.gz",
        ],
        strip_prefix = "iron-form-2.1.3",
        path = "/iron-form",
        srcs = [
            "iron-form.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_ajax",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_header_panel",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "a1e87dbeca6a9edfbef350f23f79448079f2644b6759ae8141cad2bb48974366",
        urls = [
            "https://github.com/PolymerElements/paper-header-panel/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-header-panel-2.1.0",
        path = "/paper-header-panel",
        srcs = ["paper-header-panel.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_flex_layout",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_input",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "0ee92a620b48600f18bda4f07f26d72cb9a445d8a12763a3b76721d43ae47eae",
        urls = [
            "https://github.com/PolymerElements/paper-input/archive/v2.2.1.tar.gz",
        ],
        strip_prefix = "paper-input-2.2.1",
        path = "/paper-input",
        srcs = [
            "paper-input.html",
            "paper-input-addon-behavior.html",
            "paper-input-behavior.html",
            "paper-input-char-counter.html",
            "paper-input-container.html",
            "paper-input-error.html",
            "paper-textarea.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
            "@org_polymer_iron_autogrow_textarea",
            "@org_polymer_iron_behaviors",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_iron_form_element_behavior",
            "@org_polymer_iron_input",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_button",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "c3a21e81822f824ab50fe3f36d9fa3f182fefc9884d95ebebd2c3c7878f6dd00",
        urls = [
            "https://github.com/PolymerElements/paper-button/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-button-2.1.0",
        path = "/paper-button",
        srcs = ["paper-button.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_paper_styles",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_paper_behaviors",
            "@org_polymer_paper_material",
            "@org_polymer_paper_ripple",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_a11y_keys",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "676e24990b13f10ce3eef39cb96ea42df7f7f530ae8a9c683bd435bf28932ffe",
        urls = [
            "https://github.com/PolymerElements/iron-a11y-keys/archive/v2.1.1.tar.gz",
        ],
        strip_prefix = "iron-a11y-keys-2.1.1",
        path = "/iron-a11y-keys",
        srcs = [
            "iron-a11y-keys.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
            "@org_polymer_iron_selector",
            "@org_polymer_iron_resizable_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_localstorage",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "942ee1069199d2d45941d2d16689706098ce662458cb5a1722c15ad2b29dbe9f",
        urls = [
            "https://github.com/PolymerElements/iron-localstorage/archive/v2.1.1.tar.gz",
        ],
        strip_prefix = "iron-localstorage-2.1.1",
        path = "/iron-localstorage",
        srcs = [
            "iron-localstorage.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_selector",
            "@org_polymer_iron_resizable_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_toolbar",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "6ce97a7cd55b7aadbe0fbd2c1ef768759e5f8f516645c61a2871018828dccffe",
        urls = [
            "https://github.com/PolymerElements/paper-toolbar/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-toolbar-2.1.0",
        path = "/paper-toolbar",
        srcs = ["paper-toolbar.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_paper_dropdown_menu",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "8e0fdf973abdcb7c4e3dd3bf15c48d049deb43b81012bef18b42f1db192e3473",
        urls = [
            "https://github.com/PolymerElements/paper-dropdown-menu/archive/v2.1.0.tar.gz",
        ],
        strip_prefix = "paper-dropdown-menu-2.1.0",
        path = "/paper-dropdown-menu",
        srcs = [
            "paper-dropdown-menu.html",
            "paper-dropdown-menu-icons.html",
            "paper-dropdown-menu-light.html",
            "paper-dropdown-menu-shared-styles.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
            "@org_polymer_iron_behaviors",
            "@org_polymer_iron_form_element_behavior",
            "@org_polymer_iron_icon",
            "@org_polymer_iron_iconset_svg",
            "@org_polymer_iron_validatable_behavior",
            "@org_polymer_paper_behaviors",
            "@org_polymer_paper_input",
            "@org_polymer_paper_menu_button",
            "@org_polymer_paper_ripple",
            "@org_polymer_paper_styles",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_label",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "b87a2ea440a93d988c1f45c207275272ae5ed5bbe4c8e12cca05069e7d95d309",
        urls = [
            "https://github.com/PolymerElements/iron-label/archive/v2.0.0.zip",
        ],
        strip_prefix = "iron-label-2.0.0",
        path = "/iron-label",
        srcs = [
            "iron-label.html",
        ],
        deps = [
            "@org_polymer",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_input",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "baa1f406defafe2b2e92da786567a05369412f696208d37762f3853eef745495",
        urls = [
            "https://github.com/PolymerElements/iron-input/archive/v2.1.2.tar.gz",
        ],
        strip_prefix = "iron-input-2.1.2",
        path = "/iron-input",
        srcs = ["iron-input.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_announcer",
            "@org_polymer_iron_validatable_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_autogrow_textarea",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "a6a20edde3621f6d99d5a1ec9f4ba499d02d9d8d74ddf95e29bf0966fc55e812",
        urls = [
            "https://github.com/PolymerElements/iron-autogrow-textarea/archive/v2.2.0.tar.gz",
        ],
        strip_prefix = "iron-autogrow-textarea-2.2.0",
        path = "/iron-autogrow-textarea",
        srcs = ["iron-autogrow-textarea.html"],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_behaviors",
            "@org_polymer_iron_flex_layout",
            "@org_polymer_iron_form_element_behavior",
            "@org_polymer_iron_validatable_behavior",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_dropdown",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "d64037b26cf06e0ae7f34d8f4226f0546725d9e330ff36e720376163492fb2b9",
        urls = [
            "https://github.com/PolymerElements/iron-dropdown/archive/v2.2.0.tar.gz",
        ],
        strip_prefix = "iron-dropdown-2.2.0",
        path = "/iron-dropdown",
        srcs = [
            "iron-dropdown.html",
            "iron-dropdown-scroll-manager.html",
        ],
        deps = [
            "@org_polymer",
            "@org_polymer_iron_a11y_keys_behavior",
            "@org_polymer_iron_behaviors",
            "@org_polymer_iron_overlay_behavior",
            "@org_polymer_iron_resizable_behavior",
            "@org_polymer_neon_animation",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_a11y_announcer",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "53114ceb57d9f33a7a8058488cf06450e48502e5d033adf51c91330f61620353",
        urls = [
            "http://mirror.bazel.build/github.com/PolymerElements/iron-a11y-announcer/archive/v2.0.0.tar.gz",
            "https://github.com/PolymerElements/iron-a11y-announcer/archive/v2.0.0.tar.gz",
        ],
        strip_prefix = "iron-a11y-announcer-2.0.0",
        path = "/iron-a11y-announcer",
        srcs = ["iron-a11y-announcer.html"],
        deps = ["@org_polymer"],
    )
    web_library_external(
        name = "org_polymer_iron_location",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "30197e5bf98777c565431bdca789220921ffff60e38afedd97661513adb7499c",
        urls = [
            "https://github.com/PolymerElements/iron-location/archive/v2.2.0.tar.gz",
        ],
        strip_prefix = "iron-location-2.2.0",
        path = "/iron-location",
        srcs = [
            "iron-location.html",
            "iron-query-params.html",
        ],
        deps = [
            "@org_polymer",
        ],
    )
    web_library_external(
        name = "org_polymer_iron_media_query",
        licenses = ["notice"],  # BSD 3-Clause
        sha256 = "3470dc34fed7bedc336f04c0eaffd6496a16a185849d0959d2710b61c88d4cb2",
        urls = [
            "https://github.com/PolymerElements/iron-media-query/archive/v2.1.0.zip",
        ],
        strip_prefix = "iron-media-query-2.1.0",
        path = "/iron-media-query",
        srcs = [
            "iron-media-query.html",
        ],
        deps = [
            "@org_polymer",
        ],
    )
