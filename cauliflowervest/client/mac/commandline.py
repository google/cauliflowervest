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

"""Commandline version of CauliflowerVest client."""

import getpass
import logging
import time
import urlparse

from cauliflowervest.client import base_client
from cauliflowervest.client.mac import client
from cauliflowervest.client.mac import glue
from cauliflowervest.client.mac import storage

# Actions that can be used with the --action flag
ACTION_LIST = 'list'
ACTION_DISPLAY = 'display'
ACTION_REVERT = 'revert'
ACTION_UNLOCK = 'unlock'
ACTION_ROTATE = 'rotate'
ALL_ACTIONS = {
    ACTION_LIST: 'List all volume UUIDs',
    ACTION_DISPLAY: 'Display escrowed passphrase for volume',
    ACTION_REVERT: 'Remove encryption from the specified volume',
    ACTION_UNLOCK: 'Unlock volume using escrowed recovery key',
    ACTION_ROTATE: 'Rotate escrowed recovery key for the boot volume',
}

# Possible return values from CommandLine.Execute().
RET_SUCCESS = 0  # command executed successfully
RET_MISSING_ACTION_FLAG = 2  # a required --action flag was missing
RET_UNKNOWN_ACTION_FLAG = 3  # specified action was unknown
RET_MISSING_VOLUME_FLAG = 4  # a required --volume flag was missing
RET_COULD_NOT_GET_VOLUME_INFO = 5  # problem getting volume info
RET_MISFORMATTED_VOLUME_UUID = 6  # volume UUID was formatted incorrectly
RET_COULD_NOT_REVERT_VOLUME = 7  # volume was unlocked but could not be reverted
RET_COULD_NOT_UNLOCK_VOLUME = 8  # volume could not be unlocked
RET_SERVER_COMMUNICATION_ERROR = 9  # error communicating with the server
RET_MACHINE_METADATA_ERROR = 10  # error with machine metadata
RET_BAD_ARGUMENTS = 11  # an error occurred in the glue code (bad input/options)
RET_INVALID_LOGIN_TYPE = 12  # value given with --login_type flag was unknown
RET_OAUTH2_FAILED = 13  # oauth2 login failed
RET_OTHER_ERROR = 99  # some other exception occurred


class MissingVolumeError(Exception):
  """Error raised when required volume flag is missing."""


class UnknownLoginTypeError(Exception):
  """Error raised when login_type setting is unknown."""




class CommandLine(object):
  """Command-line interface base class."""

  def __init__(self, server_url, username):
    self.server_url = server_url
    self.username = username
    self._password = None  # user password for sudo

  @property
  def password(self):
    if not self._password:
      self._password = getpass.getpass('Enter password:')
    return self._password

  @password.setter
  def password(self, value):
    self._password = value

  def Client(self):
    raise NotImplementedError('subclass must implement their own Client method')

  def Execute(self, action, volume=None):
    """Executes the specified action and returns exit code to indicate status.

    Args:
      action: string, name of action to execute.
      volume: UUID of volume to act on.
    Returns:
      an integer: one of the RET_* constants defined above.
    """
    try:
      if not action:
        print 'You must also supply an action with the --action flag.'
        print '\nValid actions are:'
        for name, desc in ALL_ACTIONS.iteritems():
          print '   "%s" -- %s' % (name, desc)
        return RET_MISSING_ACTION_FLAG
      elif action.lower() == ACTION_LIST:
        self.ListVolumes()
      elif action.lower() == ACTION_DISPLAY:
        self.DisplayPassphrase(volume)
      elif action.lower() == ACTION_REVERT:
        self.RevertVolume(volume)
      elif action.lower() == ACTION_UNLOCK:
        self.UnlockVolume(volume)
      elif action.lower() == ACTION_ROTATE:
        self.RotateRecoveryKey()
      else:
        print 'Unknown action: %s' % action
        print '\nValid actions are:'
        for name, desc in ALL_ACTIONS.iteritems():
          print '   "%s" -- %s' % (name, desc)
        return RET_UNKNOWN_ACTION_FLAG
    except MissingVolumeError as e:
      logging.warning(e.message)
      return RET_MISSING_VOLUME_FLAG
    except storage.Error as e:
      logging.warning(e.message)
      return RET_COULD_NOT_GET_VOLUME_INFO
    except storage.InvalidUUIDError as e:
      logging.warning(e.message)
      return RET_MISFORMATTED_VOLUME_UUID
    except storage.CouldNotRevertError as e:
      logging.warning(e.message)
      return RET_COULD_NOT_REVERT_VOLUME
    except storage.CouldNotUnlockError as e:
      logging.warning(e.message)
      return RET_COULD_NOT_UNLOCK_VOLUME
    except base_client.RequestError as e:
      logging.warning(e.message)
      return RET_SERVER_COMMUNICATION_ERROR
    except base_client.MetadataError as e:
      logging.warning(e.message)
      return RET_MACHINE_METADATA_ERROR
    except glue.Error as e:
      logging.warning(e.message)
      return RET_BAD_ARGUMENTS
    except UnknownLoginTypeError as e:
      logging.warning(e.message)
      return RET_INVALID_LOGIN_TYPE
    except base_client.AuthenticationError as e:
      logging.warning(e.message)
      return RET_OAUTH2_FAILED
