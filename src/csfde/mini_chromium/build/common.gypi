# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

{
  'target_defaults': {
    'xcode_settings': {
      'ALWAYS_SEARCH_USER_PATHS': 'NO',
      'DEAD_CODE_STRIPPING': 'YES',
      'DEBUG_INFORMATION_FORMAT': 'dwarf-with-dsym',
      'DEPLOYMENT_POSTPROCESSING': 'YES',
      'GCC_C_LANGUAGE_STANDARD': 'c99',         # -std=c99
      'GCC_CW_ASM_SYNTAX': 'NO',                # No -fasm-blocks
      'GCC_DYNAMIC_NO_PIC': 'NO',               # No -mdynamic-no-pic
                                                # (Equivalent to -fPIC)
      'GCC_ENABLE_CPP_EXCEPTIONS': 'NO',        # -fno-exceptions
      'GCC_ENABLE_CPP_RTTI': 'NO',              # -fno-rtti
      'GCC_ENABLE_PASCAL_STRINGS': 'NO',        # No -mpascal-strings
      # GCC_INLINES_ARE_PRIVATE_EXTERN maps to -fvisibility-inlines-hidden
      'GCC_INLINES_ARE_PRIVATE_EXTERN': 'YES',
      'GCC_OBJC_CALL_CXX_CDTORS': 'YES',        # -fobjc-call-cxx-cdtors
      'GCC_OPTIMIZATION_LEVEL': 's',
      'GCC_SYMBOLS_PRIVATE_EXTERN': 'YES',      # -fvisibility=hidden
      'GCC_THREADSAFE_STATICS': 'NO',           # -fno-threadsafe-statics
      'GCC_TREAT_WARNINGS_AS_ERRORS': 'YES',    # -Werror
      'GCC_VERSION': 'com.apple.compilers.llvm.clang.1_0',
      'GCC_WARN_ABOUT_MISSING_NEWLINE': 'YES',  # -Wnewline-eof
      # MACOSX_DEPLOYMENT_TARGET maps to -mmacosx-version-min
      'MACOSX_DEPLOYMENT_TARGET': '10.7',
      'PREBINDING': 'NO',                       # No -Wl,-prebind
      'STRIP_INSTALLED_PRODUCT': 'YES',
      'USE_HEADERMAP': 'NO',
      'WARNING_CFLAGS': [
        '-Wall',
        '-Wendif-labels',
        '-Wextra',
        # Don't warn about unused function parameters.
        '-Wno-unused-parameter',
        # Don't warn about the "struct foo f = {0};" initialization
        # pattern.
        '-Wno-missing-field-initializers',
        # clang-specific
        '-Wheader-hygiene',
      ],
    },
  },
  'xcode_settings': {
    # DON'T ADD ANYTHING NEW TO THIS BLOCK UNLESS YOU REALLY REALLY NEED IT!
    # This block adds *project-wide* configuration settings to each project
    # file.  It's almost always wrong to put things here.  Specify your
    # custom xcode_settings in target_defaults to add them to targets instead.

    # In an Xcode Project Info window, the "Base SDK for All Configurations"
    # setting sets the SDK on a project-wide basis.  In order to get the
    # configured SDK to show properly in the Xcode UI, SDKROOT must be set
    # here at the project level.
    'SDKROOT': 'macosx10.7',
  },
}
