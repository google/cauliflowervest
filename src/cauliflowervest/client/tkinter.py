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

"""CauliflowerVest client GUI module."""



import logging
import os
import pwd

import Tkinter

from cauliflowervest.client import client
from cauliflowervest.client import corestorage
from cauliflowervest.client import glue
from cauliflowervest.client import settings
from cauliflowervest.client import util
import subprocess

def RunProcess(cmd):
  p = subprocess.Popen(
      cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout, stderr, p.wait()


class Gui(object):
  """GUI written in Tkinter."""
  WIDTH = 520
  HEIGHT = 390
  MARGIN = 10
  WRAPLENGTH = WIDTH - MARGIN * 2
  ACTIONS = (
      ('verify', 'Verify Escrow'),
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
    except glue.OptionError, e:
      self.ShowFatalError(e)
    else:
      if skip_welcome:
        self._EncryptAuth()
      else:
        self._EncryptIntro()
    self.root.mainloop()

  def ShowFatalError(self, message):
    logging.exception(message)
    self._PrepTop()
    Tkinter.Label(
        self.top_frame, text=unicode(message), wraplength=self.WRAPLENGTH
        ).pack(fill=Tkinter.Y, expand=True)
    Tkinter.Button(self.top_frame, text='Ok', command=self.root.quit).pack()

  def EncryptedVolumePrompt(self, error_message=None):
    """Prompt for any "unlock" kind of action."""
    if isinstance(error_message, Tkinter.Event):
      error_message = None
    self._PrepTop()
    if error_message:
      Tkinter.Label(self.top_frame, text=error_message).pack()

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

    Tkinter.Label(
        self.top_frame, text='Authenticate:').pack(anchor=Tkinter.W)
    self._AuthPrompt(
        self.top_frame, cont_func=self._EncryptedVolumeAction
        ).pack(fill=Tkinter.Y, expand=True)
    Tkinter.Button(
        self.top_frame, text='Continue', command=self._EncryptedVolumeAction
        ).pack()

    self.root.mainloop()

  def _PlainVolumeAction(self, *unused_args):
    try:
      credentials = self._Authenticate(self._EncryptAuth)
    except glue.Error:
      return
    username, password = credentials[0:2]
    # In case username is actually an email:
    username = username.split('@', 1)[0]

    self._PrepTop()
    Tkinter.Label(
        self.top_frame, text='Applying encryption...'
        ).pack(fill=Tkinter.BOTH, expand=True)
    self.root.update()

    try:
      volume_uuid, recovery_token = glue.ApplyEncryption(
          self.fvclient, username, password)
    except glue.Error:
      return self.ShowFatalError(glue.ENCRYPTION_FAILED_MESSAGE)

    try:
      self.fvclient.UploadPassphrase(volume_uuid, recovery_token)
    except glue.client.Error:
      return self.ShowFatalError(glue.ESCROW_FAILED_MESSAGE)

    self._PrepTop()
    # 8 is a magic number ...
    Tkinter.Label(
        self.top_frame, text=glue.ENCRYPTION_SUCCESS_MESSAGE
        ).pack(fill=Tkinter.Y, expand=True)

    cmd = ['ps', 'auwx']
    process_list, unused_err, ret = RunProcess(cmd)
    finder = '/System/Library/CoreServices/Finder.app/Contents/MacOS/Finder\n'
    if (ret == 0 and process_list and finder in process_list) or ret != 0:
      Tkinter.Button(
          self.top_frame, text='Restart now', command=self._RestartNow
          ).pack()
      # TODO(user): Ensure the user doesn't close the window and never reboot.
    else:
      Tkinter.Button(
          self.top_frame, text='Ok', command=self.root.quit
          ).pack()

  def _EncryptedVolumeAction(self, *unused_args):
    try:
      self._Authenticate(self.EncryptedVolumePrompt)
    except glue.Error:
      return

    action_dict = dict(self.ACTIONS)
    self._PrepTop()
    Tkinter.Label(
        self.top_frame, text='Doing: %s...' % action_dict[self.action.get()]
        ).pack(fill=Tkinter.BOTH, expand=True)
    self.root.update()

    volume_uuid = self.unlock_volume.get()
    message = None

    try:
      if self.action.get() == self.ACTIONS[0][0]:
        if self.fvclient.VerifyEscrow(volume_uuid):
          message = 'A recovery passphrase is properly escrowed.'
        else:
          message = 'WARNING: A recovery passphrase is NOT escrowed.'
      else:
        passphrase = self.fvclient.RetrievePassphrase(volume_uuid)
    except client.Error, e:
      return self.ShowFatalError(e)

    if self.action.get() == self.ACTIONS[1][0]:
      corestorage.RevertVolume(volume_uuid, passphrase)
      message = 'Volume reverted successfully: %s' % volume_uuid
    elif self.action.get() == self.ACTIONS[2][0]:
      corestorage.UnlockVolume(volume_uuid, passphrase)
      message = 'Volume unlocked successfully: %s' % volume_uuid
    elif self.action.get() == self.ACTIONS[3][0]:
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
      self._PrepTop()
      Tkinter.Label(
          self.top_frame, text=message, wraplength=self.WRAPLENGTH
          ).pack(fill=Tkinter.BOTH, expand=True)
      Tkinter.Button(
          self.top_frame, text='Ok', command=self.root.quit
          ).pack()

  def _EncryptAuth(self, error_message=None):
    if isinstance(error_message, Tkinter.Event):
      error_message = None

    self._PrepTop()
    Tkinter.Label(
        self.top_frame,
        text='Only this user will be able to unlock the encrypted drive.'
        ).pack()
    if error_message:
      Tkinter.Label(
          self.top_frame, text=error_message, wraplength=self.WRAPLENGTH).pack()
    self._AuthPrompt(
        self.top_frame, cont_func=self._PlainVolumeAction
        ).pack(fill=Tkinter.Y, expand=True)
    Tkinter.Button(
        self.top_frame, text='Encrypt', command=self._PlainVolumeAction).pack()

  def _EncryptIntro(self):
    self._PrepTop()
    Tkinter.Label(
        self.top_frame, text=settings.INTRO_TEXT, wraplength=self.WRAPLENGTH
        ).pack(fill=Tkinter.BOTH, expand=True)
    b = Tkinter.Button(
        self.top_frame, text='Continue', takefocus=True,
        command=self._EncryptAuth, default=Tkinter.ACTIVE)
    b.pack()
    b.focus_set()  # This only makes space work, so ...
    b.bind('<Return>', self._EncryptAuth)

  def _PrepTop(self):
    """Prepare the replaceable top frame that contains the active section."""
    if self.top_frame:
      self.top_frame.destroy()
    self.top_frame = Tkinter.Frame(self.root, borderwidth=self.MARGIN)
    self.top_frame.pack(fill=Tkinter.BOTH, expand=True)

  def _RestartNow(self):
    RunProcess(
        ['/usr/bin/osascript',
        '-e', 'tell application "Finder" to restart'])


class GuiClientLogin(Gui):
  """GUI plumbing class that does authentication with clientlogin."""

  def _AppPassHelp(self):
    dialog = Tkinter.Toplevel(borderwidth=self.MARGIN)
    dialog.title = 'Application Specific Password Help'

    Tkinter.Label(dialog, text=(
        'If your account has second-factor authentication enabled, you must '
        'provide an application-specific password in order to connect to the '
        'server.  You must also provide your normal password for encryption. '
        ), wraplength=self.WRAPLENGTH).pack()
    Tkinter.Label(dialog, text=(
        'If not, you can just provide your regular password and leave this '
        'field empty.'
        ), wraplength=self.WRAPLENGTH).pack()

    Tkinter.Button(dialog, text='Ok', command=dialog.destroy).pack()

  def _Authenticate(self, error_func):
    """Do authentication, return an escrow client.

    Args:
      error_func: callable, passed a message when there is an error.
    Side effects:
      Sets self.fvclient to an instance of client.FileVaultClient().
    Returns:
      Tuple of strs, (username, password, google_email, google_pass)
    Raises:
      glue.Error: If the client cannot be established/authenticated.
    """
    username, password, google_email, google_pass = (
        self.input_user.get(), self.input_pass.get(),
        self.input_email.get(), self.input_google_pass.get())
    if not username or not password or not google_email or not google_pass:
      msg = 'All fields are required'
      error_func(msg)
      raise glue.Error(msg)

    self._PrepTop()
    Tkinter.Label(
        self.top_frame, text='Logging in...'
        ).pack(fill=Tkinter.BOTH, expand=True)
    self.root.update()

    try:
      self.fvclient = glue.GetEscrowClient(
          self.server_url, (google_email, google_pass or password),
          login_type='clientlogin')
    except glue.Error, e:
      error_func(unicode(e))
      raise

    return username, password, google_email, google_pass

  def _AuthPrompt(self, root, cont_func):
    """Reusable authentication prompt fields."""
    grid = Tkinter.Frame(root)

    Tkinter.Label(
        grid, text='Google Account Email', justify=Tkinter.RIGHT).grid(
            column=0, row=0)
    self.input_email = Tkinter.Entry(grid)
    self.input_email.grid(column=1, row=0)

    Tkinter.Label(
        grid, text='Google Account Password', wraplength=140
        ).grid(column=0, row=1)
    self.input_google_pass = Tkinter.Entry(grid, show='*')
    self.input_google_pass.grid(column=1, row=1)

    Tkinter.Label(
        grid, text='Local Username', justify=Tkinter.RIGHT).grid(
            column=0, row=2)
    self.input_user = Tkinter.Entry(grid)
    self.input_user.grid(column=1, row=2)

    Tkinter.Label(
        grid, text='Local Password', justify=Tkinter.RIGHT).grid(
            column=0, row=3)
    self.input_pass = Tkinter.Entry(grid, show='*')
    self.input_pass.grid(column=1, row=3)

    Tkinter.Button(
        grid, text='Help', command=self._AppPassHelp
        ).grid(column=2, row=2)

    self.input_email.focus_set()
    self.input_pass.bind('<Return>', cont_func)

    return grid

