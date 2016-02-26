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
#
#

"""CauliflowerVest client GUI module."""



import logging
import os
import pwd
import threading
import time
import urlparse

import Tkinter


from cauliflowervest.client import base_client
from cauliflowervest.client import settings
from cauliflowervest.client import util
from cauliflowervest.client.mac import client
from cauliflowervest.client.mac import corestorage
from cauliflowervest.client.mac import glue

import subprocess
def RunProcess(cmd):
  p = subprocess.Popen(
      cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout, stderr, p.wait()


class Countdown(threading.Thread):
  """Thread to update a Tkinter label with seconds remaining in a countdown."""

  def __init__(self, label=None, seconds=10, termination_callback=None):
    self.label = label
    self.seconds = seconds
    self.original_text = label['text']
    self.termination_callback = termination_callback
    super(Countdown, self).__init__()

  def run(self):
    for remaining in range(self.seconds, 0, -1):
      self.label['text'] = '%s (%s)' % (self.original_text, remaining)
      time.sleep(1)
    self.termination_callback()


class Gui(object):
  """GUI written in Tkinter."""
  WIDTH = 520
  HEIGHT = 390
  MARGIN = 10
  WRAPLENGTH = WIDTH - MARGIN * 2
  ACTIONS = (
      ('revert', 'Revert Volume'),
      ('unlock', 'Unlock Volume'),
      ('display', 'Display Passphrase'),
      )

  def __init__(self, server_url):
    self.server_url = server_url

    # This is the top-level container that is destroyed and recreated to
    # "switch pages".  See _PrepTop().
    self.top_frame = None

    self.username = pwd.getpwuid(os.getuid()).pw_name  # current user name
    self.password = None

    self.root = Tkinter.Tk()
    self.root.title('CauliflowerVest')
    # Set our fixed size, and center on the screen.
    self.root.geometry('%dx%d+%d+%d' % (
        self.WIDTH, self.HEIGHT,
        self.root.winfo_screenwidth() / 2 - self.WIDTH / 2,
        self.root.winfo_screenheight() / 2 - self.HEIGHT / 2,
        ))

    # Override Tk's default error handling.
    self.root.report_callback_exception = (
        lambda _1, exc, *_2, **_3: self.ShowFatalError(exc))

    # Lame hack around OSX focus issue.  http://goo.gl/9U0Vg
    util.Exec((
        '/usr/bin/osascript', '-e',
        'tell app "Finder" to set frontmost of process "Python" to true'))
    self.top_frame = None

  def PlainVolumePrompt(self, skip_welcome=False):
    """Initial GUI prompt when the volume is plain text."""
    try:
      glue.CheckEncryptionPreconditions()
    except glue.OptionError as e:
      self.ShowFatalError(e)
    else:
      if skip_welcome:
        self._EncryptAuth()
      else:
        self._EncryptIntro()
    self.root.mainloop()

  def ShowFatalError(self, message):
    logging.exception(message)
    self._PrepTop(message)
    Tkinter.Button(self.top_frame, text='OK', command=self.root.quit).pack()

  def EncryptedVolumePrompt(self, error_message=None):
    """Prompt for any "unlock" kind of action."""
    if isinstance(error_message, Tkinter.Event):
      error_message = None
    self._PrepTop(error_message)

    _, encrypted_volumes, _ = corestorage.GetStateAndVolumeIds()
    Tkinter.Label(
        self.top_frame,
        text='Pick one of the following encrypted volumes:').pack(
            anchor=Tkinter.W)
    self.unlock_volume = Tkinter.StringVar()
    self.unlock_volume.set(encrypted_volumes[0])
    for volume in encrypted_volumes:
      size = corestorage.GetVolumeSize(volume)
      text = '%s %s' % (volume, size)
      Tkinter.Radiobutton(
          self.top_frame, text=text, variable=self.unlock_volume, value=volume
          ).pack(anchor=Tkinter.W)

    Tkinter.Label(
        self.top_frame, text='Pick an action:').pack(anchor=Tkinter.W)
    self.action = Tkinter.StringVar()
    self.action.set(self.ACTIONS[0][0])
    for action, action_text in self.ACTIONS:
      Tkinter.Radiobutton(
          self.top_frame, variable=self.action,
          text=action_text, value=action
          ).pack(anchor=Tkinter.W)

    Tkinter.Button(
        self.top_frame, text='Continue', command=self._EncryptedVolumeAction
        ).pack()

    self.root.mainloop()

  def _PlainVolumeAction(self, *unused_args):
    user, passwd = self.input_user.get(), self.input_pass.get()

    try:
      client_ = self._Authenticate(self._EncryptAuth)
      if not client_: return
    except glue.Error:
      return

    self._PrepTop('Applying encryption...')

    try:
      volume_uuid, recovery_token = glue.ApplyEncryption(client_, user, passwd)
    except glue.Error:
      return self.ShowFatalError(glue.ENCRYPTION_FAILED_MESSAGE)

    try:
      client_.UploadPassphrase(volume_uuid, recovery_token)
    except base_client.Error:
      return self.ShowFatalError(glue.ESCROW_FAILED_MESSAGE)

    self._PrepTop(glue.ENCRYPTION_SUCCESS_MESSAGE)

    cmd = ['ps', 'auwx']
    process_list, unused_err, ret = RunProcess(cmd)
    finder = '/System/Library/CoreServices/Finder.app/Contents/MacOS/Finder\n'
    if (ret == 0 and process_list
        and finder in process_list) or ret != 0:
      btn = Tkinter.Button(
          self.top_frame, text='Restart now', command=self._RestartNow)
      btn.pack()
      countdown = Countdown(label=btn, termination_callback=self._RestartNow)
      countdown.start()
    else:
      btn = Tkinter.Button(self.top_frame, text='OK', command=self.root.quit,
                           default=Tkinter.ACTIVE)
      btn.bind('<Return>', lambda _: self.root.quit())
      btn.pack()
      btn.focus()
      countdown = Countdown(label=btn, termination_callback=self.root.quit)
      countdown.start()

  def _EncryptedVolumeAction(self, *unused_args):
    try:
      client_ = self._Authenticate(self.EncryptedVolumePrompt)
    except glue.Error as e:
      return self.ShowFatalError(e)

    action_dict = dict(self.ACTIONS)
    self._PrepTop('Doing: %s...' % action_dict[self.action.get()])

    volume_uuid = self.unlock_volume.get()
    message = None

    try:
      passphrase = client_.RetrieveSecret(volume_uuid)
    except base_client.Error as e:
      return self.ShowFatalError(e)

    if self.action.get() == self.ACTIONS[0][0]:
      corestorage.RevertVolume(volume_uuid, passphrase)
      message = 'Volume reverted successfully: %s' % volume_uuid
    elif self.action.get() == self.ACTIONS[1][0]:
      corestorage.UnlockVolume(volume_uuid, passphrase)
      message = 'Volume unlocked successfully: %s' % volume_uuid
    elif self.action.get() == self.ACTIONS[2][0]:
      self._PrepTop()
      Tkinter.Label(self.top_frame, text='').pack(fill=Tkinter.Y, expand=True)
      Tkinter.Label(
          self.top_frame,
          text='Here is the recovery token.  Be careful with it.').pack()
      e = Tkinter.Entry(self.top_frame, width=self.WRAPLENGTH)
      e.pack(fill=Tkinter.Y, expand=False)
      e.insert(Tkinter.END, passphrase)
      e.configure(state='readonly')
      Tkinter.Label(self.top_frame, text='').pack(fill=Tkinter.Y, expand=True)
      return

    if message:
      self._PrepTop(message)
      Tkinter.Button(
          self.top_frame, text='OK', command=self.root.quit
          ).pack()

  def _Authenticate(self, error_func):
    """Do authentication, return an escrow client.

    Args:
      error_func: callable, passed a message when there is an error.
    Returns:
      A client.CauliflowerVestClient instance.
    Raises:
      glue.Error: If the client cannot be established/authenticated.
    """
    raise NotImplementedError()

  def _AuthPrompt(self, root, cont_func):
    """Reusable authentication prompt fields."""
    Tkinter.Label(
        self.top_frame, text='\nAuthenticate:').pack(anchor=Tkinter.W)

    grid = Tkinter.Frame(root)

    Tkinter.Label(grid, text='Username').grid(column=0, row=0)
    self.input_user = Tkinter.Entry(grid)
    self.input_user.grid(column=1, row=0)

    Tkinter.Label(grid, text='Password').grid(column=0, row=1)
    self.input_pass = Tkinter.Entry(grid, show='*')
    self.input_pass.grid(column=1, row=1)
    self.input_pass.bind('<Return>', cont_func)

    if self.username:
      self.input_user.insert(0, self.username)
      self.input_pass.focus_set()
    else:
      self.input_user.focus_set()

    return grid

  def _EncryptAuth(self, error_message=None):
    if isinstance(error_message, Tkinter.Event):
      error_message = None

    self._PrepTop()
    if True:
      Tkinter.Label(
          self.top_frame,
          text='Only this user will be able to unlock the encrypted drive.'
          ).pack()

    if error_message:
      Tkinter.Label(
          self.top_frame, text=error_message, wraplength=self.WRAPLENGTH
          ).pack()
    self._AuthPrompt(
        self.top_frame, cont_func=self._PlainVolumeAction
        ).pack(fill=Tkinter.Y, expand=True)
    Tkinter.Button(
        self.top_frame, text='Encrypt', command=self._PlainVolumeAction).pack()

  def _EncryptIntro(self):
    self._PrepTop(settings.INTRO_TEXT)
    b = Tkinter.Button(
        self.top_frame, text='Continue', takefocus=True,
        command=self._EncryptAuth, default=Tkinter.ACTIVE)
    b.pack()
    b.focus_set()  # This only makes space work, so ...
    b.bind('<Return>', self._EncryptAuth)

  def _PrepTop(self, message=None):
    """Prepare the replaceable top frame that contains the active section."""
    if self.top_frame:
      self.top_frame.destroy()
    self.top_frame = Tkinter.Frame(self.root, borderwidth=self.MARGIN)
    self.top_frame.pack(fill=Tkinter.BOTH, expand=True)

    if message:
      Tkinter.Label(
          self.top_frame, text=unicode(message), wraplength=self.WRAPLENGTH
          ).pack(fill=Tkinter.BOTH, expand=True)
      self.root.update()

  def _RestartNow(self):
    RunProcess(
        ['/usr/bin/osascript',
        '-e', 'tell application "Finder" to restart'])

  def _ShowLoggingInMessage(self):
    self._PrepTop('Logging in...')


class GuiOauth(Gui):
  """Subclass of `Gui` which authenticates via OAuth2."""

  def _Authenticate(self, error_func):
    self._ShowLoggingInMessage()

    try:
      credentials = base_client.GetOauthCredentials()
    except RuntimeError as e:
      error_func(unicode(e))
      return

    opener = base_client.BuildOauth2Opener(credentials)
    client_ = client.FileVaultClient(self.server_url, opener)

    try:
      client_.GetAndValidateMetadata()
    except base_client.MetadataError as e:
      error_func(unicode(e))
      return

    return client_
