#!/usr/bin/env python
# 
# Copyright 2010 Google Inc. All Rights Reserved.
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
#

"""Generates a Google App Engine appid based on various settings."""




import settings


def GenerateAppID():
  """Returns a Google App Engine appid based on subdomain + domain configs."""
  if settings.DOMAIN == 'appspot.com':
    return settings.SUBDOMAIN
  else:
    return '%s:%s' % (settings.DOMAIN, settings.SUBDOMAIN)


def main():
  print GenerateAppID()


if __name__ == '__main__':
  main()
