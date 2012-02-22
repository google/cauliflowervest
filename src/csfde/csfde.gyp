# Copyright (c) 2011 Google Inc. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

{
  'includes': [
    'mini_chromium/build/common.gypi',
  ],
  'targets': [
    {
      'target_name': 'csfde',
      'type': 'executable',
      'include_dirs': [
        'mini_chromium',
      ],
      'sources': [
        'csfde.mm',
        'mini_chromium/base/basictypes.h',
        'mini_chromium/base/compiler_specific.h',
        'mini_chromium/base/logging.h',
        'mini_chromium/base/logging.cc',
        'mini_chromium/base/mac/scoped_cftyperef.h',
        'mini_chromium/base/mac/scoped_nsautorelease_pool.h',
        'mini_chromium/base/mac/scoped_nsautorelease_pool.mm',
        'mini_chromium/base/memory/scoped_nsobject.h',
        'mini_chromium/base/safe_strerror_posix.h',
        'mini_chromium/base/safe_strerror_posix.cc',
        'mini_chromium/build/build_config.h',
        'mini_chromium/chrome/browser/mac/scoped_ioobject.h',
      ],
      'libraries': [
        '$(SDKROOT)/System/Library/Frameworks/CoreFoundation.framework',
        '$(SDKROOT)/System/Library/Frameworks/DiskArbitration.framework',
        '$(SDKROOT)/System/Library/Frameworks/Foundation.framework',
        '$(SDKROOT)/System/Library/Frameworks/IOKit.framework',
        '$(SDKROOT)/System/Library/Frameworks/OpenDirectory.framework',
        '$(SDKROOT)/System/Library/PrivateFrameworks/DiskManagement.framework',
        '$(SDKROOT)/System/Library/PrivateFrameworks/EFILogin.framework',
        '$(SDKROOT)/usr/lib/libcsfde.dylib',
      ],
      'xcode_settings': {
        'ARCHS': [
          'x86_64',
          'i386',
        ],
        'FRAMEWORK_SEARCH_PATHS': [
          '$(SDKROOT)/System/Library/PrivateFrameworks',
        ],
      },
    },
  ],
}
