#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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
#

try:
  from setuptools import setup, find_packages
except ImportError:
  print 'required Python setuptools is missing.'
  print 'install from http://pypi.python.org/pypi/setuptools'
  raise SystemExit(1)


REQUIRE = [
    'pyasn1==0.1.9',            # version: fixes pyasn1_modules 0.0.5 dep
    'oauth2client',
]

# should be in sync with PACKAGE_DEPS in postflight
REQUIRE_SETUP = [
    'pyyaml',
    'google_apputils',
    'python-dateutil>=1.4,<2',  # required by: google_apputils
    'setuptools>=0.6.49',        # version: fix bugs in old version on Leopard
]
REQUIRE_TESTS = REQUIRE + [
    'jinja2',
    'mock==1.0.1',              # mock 1.2+ require setuptools>=17.1
    'mox>=0.5.3',
    'pillow',
    'pycrypto',
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
    version='0.10.2',
    url='https://github.com/google/cauliflowervest',
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
