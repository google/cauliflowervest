#!/bin/bash
#
# Copyright 2012 Google Inc.  All Rights Reserved.
#
# Creates a Google App Engine deployable bundle of Cauliflower Vest code.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

ROOT=$1
BUNDLE_ROOT=$ROOT/gae_bundle/
SRC_REL_PATH=../src/cauliflowervest/
SERVER_REL_PATH=$SRC_REL_PATH/server/
SUBDIR=cauliflowervest

# Create Google App Engine bundle directory.
rm -rf $BUNDLE_ROOT
mkdir -p $BUNDLE_ROOT/$SUBDIR
touch $BUNDLE_ROOT/__init__.py
touch $BUNDLE_ROOT/$SUBDIR/__init__.py

# Symlink the server src.
ln -s ../$SRC_REL_PATH/server $BUNDLE_ROOT/$SUBDIR/server

# Symlink the shared settings file inside the app directory.
ln -s ../$SRC_REL_PATH/settings.py $BUNDLE_ROOT/$SUBDIR/settings.py

# Symlink necessary files at the root of the bundle.
ln -s $SERVER_REL_PATH/appengine_config.py $BUNDLE_ROOT/appengine_config.py
ln -s $SERVER_REL_PATH/app.yaml $BUNDLE_ROOT/app.yaml
ln -s $SERVER_REL_PATH/index.yaml $BUNDLE_ROOT/index.yaml
ln -s $SERVER_REL_PATH/cron.yaml $BUNDLE_ROOT/cron.yaml
ln -s $SERVER_REL_PATH/main.py $BUNDLE_ROOT/main.py

# Create symlinks to python egg files.
if [ -d pyasn1-*.egg ]; then
  cd ${BUNDLE_ROOT} && ln -f -s ../pyasn1-*.egg/pyasn1 pyasn1 ;
elif [ -f pyasn1-*.egg ]; then
  cd ${BUNDLE_ROOT} && unzip ../pyasn1-*.egg ;
else
  ./link_module.sh pyasn1 || ( echo Cannot resolve pyasn1 ; exit 1 ) ;
fi
cd ${BUNDLE_ROOT} && ln -f -s ../build/keyczar keyczar

