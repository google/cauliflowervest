#!/usr/bin/env python
# 
# Copyright 2011 Google Inc. All Rights Reserved.
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
# #

try:
  from setuptools import setup, find_packages
except ImportError:
  print 'required Python setuptools is missing.'
  print 'install from http://pypi.python.org/pypi/setuptools'
  raise SystemExit(1)


REQUIRE = [
    'pyasn1',                   # required by: pycrypto
]
REQUIRE_SETUP = [
    'google_apputils>=0.2',
    'python-dateutil>=1.4,<2',  # required by: google_apputils
    'setuptools>=0.6c9',        # version: fix bugs in old version on Leopard
]
REQUIRE_TESTS = REQUIRE + [
    'django',
    'mox>=0.5.3',
    'pycrypto',
    'pyyaml',
    'simplejson',
    'webob',
    'webapp2',
]

CV_STUBS = [
    ('cauliflowervest', 'RunCauliflowerVest'),
]
CV_ENTRY_POINTS = ['%s = cauliflowervest.stubs:%s' % s for s in CV_STUBS]

setup(
    name='cauliflowervest',
    version='0.9.4',
    url='http://code.google.com/p/cauliflowervest',
    license='Apache 2.0',
    description='Key escrow for full disk encryption',
    author='Google',
    author_email='cauliflowervest-eng@googlegroups.com',

    packages=find_packages('src', exclude=['tests']),
    package_dir={'': 'src'},
    package_data={
        '': ['*.zip'],
    },
    include_package_data=True,

    entry_points={
        'console_scripts': CV_ENTRY_POINTS,
    },

    setup_requires=REQUIRE_SETUP,
    install_requires=REQUIRE,
    tests_require=REQUIRE_TESTS,
    google_test_dir='src/tests',
)