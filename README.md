## Overview

[Cauliflower Vest](../../wiki/ThatName) is a recovery key escrow solution.  The project initially started with end-to-end Mac OS X FileVault 2 support, and later added support for BitLocker (Windows), LUKS (Linux), and Duplicity. The goal of this project is to streamline cross-platform enterprise management of disk encryption technologies.

Cauliflower Vest offers the ability to:
  * Forcefully enable FileVault 2 encryption.
  * Automatically escrow recovery keys to a secure Google App Engine server.
  * Delegate secure access to recovery keys so that volumes may be unlocked or reverted.
  * Sync BitLocker recovery keys from Active Directory.

Components:

  * A Google App Engine based service which receives and securely escrows recovery keys.
  * A GUI client running on the OS X user machines, which enables FileVault 2 encryption, obtains the recovery key, and sends it to the escrow service.
  * A CLI tool, [csfde](../../wiki/Csfde), which activates FileVault 2 encryption on OS X 10.7 Lion, which may be used independently of the GUI client.
  * A CLI tool which runs on Linux, for use with LUKS and Duplicity.
  * A script to sync BitLocker recovery keys from Active Directory to Clipper.

## Getting Started

Full source is available for all components.

To get started, begin with the [Introduction](../../wiki/Introduction) wiki page.

### Office Hours

The Cauliflower Vest engineering team will host office hours every other Monday from 11am to 1pm Eastern Time. Office hours are available as a video conference via Google+ Hangout, or on the irc network [freenode](http://freenode.net). Feel free to use or not use a webcam for the hangout.

Next office hours are **Mon Nov 3**, 11am-1pm US/Eastern.

Join the Google+ Hangout here (new URL for each session): ...

We will simultaneously be present on [freenode](http://freenode.net/) in:

> ` #google-corpeng `

Feel free to join and/or email the discussion list with questions at [cauliflowervest-discuss@googlegroups.com](mailto:cauliflowervest-discuss@googlegroups.com).
To reach only engineers on the project, email [cauliflowervest-eng@googlegroups.com](mailto:cauliflowervest-eng@googlegroups.com).

<br />

<img src='https://raw.githubusercontent.com/google/cauliflowervest/master/res/cauliflower_vest_logo.png?token=9258614__eyJzY29wZSI6IlJhd0Jsb2I6Z29vZ2xlL2NhdWxpZmxvd2VydmVzdC9tYXN0ZXIvcmVzL2NhdWxpZmxvd2VyX3Zlc3RfbG9nby5wbmciLCJleHBpcmVzIjoxNDE0MTYzOTgzfQ%3D%3D--c6b6f034a6a1476661993ac550fa35182825ba5c' />
<p>Thanks to [Dorothy Marczak](https://plus.google.com/106286115972636321533/about) for the logo.</p>
