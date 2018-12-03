![ci](https://travis-ci.org/google/cauliflowervest.svg?branch=master)
## Overview
**Note: OAUTH_CLIENT_ID moved from src/cauliflowervest/client/settings.py to
cauliflowervest/settings.py**

[Cauliflower Vest](../../wiki/ThatName) is a recovery key escrow solution.
The project initially started with end-to-end Mac OS X FileVault 2 support,
and later added support for BitLocker (Windows), LUKS (Linux), Duplicity, and
Firmware/BIOS passwords (Mac & Linux). The goal of this project is to streamline
cross-platform enterprise management of disk encryption technologies.

Cauliflower Vest offers the ability to:
  * Forcefully enable FileVault 2 encryption.
  * Automatically escrow recovery keys to a secure Google App Engine server.
  * Delegate secure access to recovery keys so that volumes may be unlocked or
    reverted.
  * Sync BitLocker recovery keys from Active Directory.

Components:

  * A Google App Engine based service which receives and securely escrows
    recovery keys.
  * A GUI client running on the OS X user machines, which enables
    FileVault 2 encryption, obtains the recovery key, and sends it to the escrow
    service.

  * A CLI tool which runs on Linux, for use with LUKS and Duplicity.
  * A script to sync BitLocker recovery keys from Active Directory.

## Getting Started

Full source is available for all components.

To get started, begin with the [Introduction](../../wiki/Introduction)
wiki page.

## Warning

Upon releasing the [update](https://github.com/google/cauliflowervest/commit/915128d42e2b949662e9e1b29e6c7a09926aab2d)
to App Engine, start the schema update (/ui/#/admin/) otherwise
search and key retrieval will break. Progress can be
monitored in [App Engine logs](http://console.cloud.google.com/logs).
Logs will contain
```
UpdateSchema complete for VOLUME_TYPE with N updates!
```
for each volume type after successful migration.

### Contact

Please search, join, and/or email the discussion list with questions at [cauliflowervest-discuss@googlegroups.com](https://groups.google.com/forum/#!forum/cauliflowervest-discuss).
To reach only engineers on the project, email
cauliflowervest-eng@googlegroups.com.



![](https://raw.githubusercontent.com/google/cauliflowervest/master/res/cauliflower_vest_logo.png)

Thanks to [Dorothy Marczak](https://plus.google.com/106286115972636321533/about)
for the logo.
