# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Module to handle searching for escrowed passphrases."""

import httplib
import os
import urllib
from google.appengine.api import users

from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.handlers import passphrase_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import errors
from cauliflowervest.server.models import util as models_util


MAX_PASSPHRASES_PER_QUERY = 250


def _PassphrasesForQuery(model, search_field, value, prefix_search=False):
  """Search a model for matching the string query.

  Args:
    model: base.BasePassphrase model.
    search_field: str, search field name.
    value: str, search term.
    prefix_search: boolean, True to perform a prefix search, False otherwise.
  Returns:
    list of entities of type base.BasePassphrase.
  """
  query = model.all()

  if search_field == 'created_by':
    if '@' not in value:
      value = '%s@%s' % (value, os.environ.get('AUTH_DOMAIN'))
    value = users.User(value)
  elif search_field == 'hostname':
    value = model.NormalizeHostname(value)

  if prefix_search and search_field != 'created_by':
    if search_field == 'owner':
      search_field = 'owners'
    query.filter('%s >=' % search_field, value).filter(
        '%s <' % search_field, value + u'\ufffd')
  elif search_field == 'owner' and not prefix_search:
    if '@' not in value:
      value = '%s@%s' % (value, settings.DEFAULT_EMAIL_DOMAIN)
    query.filter('owners =', value)
  else:
    query.filter(search_field + ' =', value)

  if (model.ESCROW_TYPE_NAME == permissions.TYPE_PROVISIONING
      and search_field == 'created_by'):
    query.order('-created')
  passphrases = query.fetch(MAX_PASSPHRASES_PER_QUERY)
  passphrases.sort(key=lambda x: x.created, reverse=True)
  return passphrases


class Search(passphrase_handler.PassphraseHandler):
  """Handler for /search URL."""

  def get(self):
    """Handles GET requests."""
    if self.request.get('json', '0') != '1':
      search_type = self.request.get('search_type')
      field1 = urllib.quote(self.request.get('field1'))
      value1 = urllib.quote(self.request.get('value1').strip())
      prefix_search = urllib.quote(self.request.get('prefix_search', '0'))

      if search_type and field1 and value1:
        self.redirect(
            '/ui/#/search/%s/%s/%s/%s' % (
                search_type, field1, value1, prefix_search))
      else:
        self.redirect('/ui/', permanent=True)
      return

    tag = self.request.get('tag', 'default')
    search_type = self.request.get('search_type')
    field1 = self.request.get('field1')
    value1 = self.request.get('value1').strip()
    prefix_search = self.request.get('prefix_search', '0') == '1'

    try:
      model = models_util.TypeNameToModel(search_type)
    except ValueError:
      raise passphrase_handler.InvalidArgumentError(
          'Invalid search_type %s' % search_type)

    if not (field1 and value1):
      raise base_handler.InvalidArgumentError('Missing field1 or value1')

    # Get the user's search and retrieve permissions for all permission types.
    search_perms = base_handler.VerifyAllPermissionTypes(permissions.SEARCH)
    retrieve_perms = base_handler.VerifyAllPermissionTypes(
        permissions.RETRIEVE_OWN)
    retrieve_created = base_handler.VerifyAllPermissionTypes(
        permissions.RETRIEVE_CREATED_BY)

    # user is performing a search, ensure they have permissions.
    if (not search_perms.get(search_type)
        and not retrieve_perms.get(search_type)
        and not retrieve_created.get(search_type)):
      raise errors.AccessDeniedError('User lacks %s permission' % search_type)

    try:
      passphrases = _PassphrasesForQuery(model, field1, value1, prefix_search)
    except ValueError:
      self.error(httplib.NOT_FOUND)
      return

    skipped = False
    if not search_perms.get(search_type):
      results_len = len(passphrases)
      email = base.GetCurrentUser().user.email()
      passphrases = [x for x in passphrases if email in x.owners]
      skipped = len(passphrases) != results_len
    too_many_results = len(passphrases) >= MAX_PASSPHRASES_PER_QUERY

    passphrases = [v.ToDict(skip_secret=True)
                   for v in passphrases if v.tag == tag]
    if model.ALLOW_OWNER_CHANGE:
      for passphrase in passphrases:
        if not passphrase['active']:
          continue
        link = '/api/internal/change-owner/%s/%s/' % (
            search_type, passphrase['id'])
        passphrase['change_owner_link'] = link

    self.response.out.write(util.ToSafeJson({
        'passphrases': passphrases,
        'too_many_results': too_many_results,
        'results_access_warning': skipped,
    }))
