#!/usr/bin/env python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

"""Configurable settings module for the client."""




INTRO_TEXT = """
Cauliflower Vest will encrypt the entire disk on this Mac.

It will also back up the recovery key for emergency purposes, like if you
forget your password.  It's very important that disk encryption is enabled
by Cauliflower Vest and *NOT* manually, to ensure that the recovery key is
backed up.

Upon success, you will see a final dialog box indicating that Cauliflower
Vest has encrypted your drive, stored the recovery key remotely, and that
you should restart.

If you do not see this final success message, you may not be secure. Please
contact Tech Support if you are not sure.
""".strip()



ROOT_CA_CERT_CHAIN_PEM_FILE_PATH = '/usr/local/cauliflowervest/roots.pem'

# These values must be filled in for authentication to work!
OAUTH_CLIENT_ID = ''
OAUTH_CLIENT_SECRET = ''

