"""Cloud KMS helper lib.

See README for setup and explanation of KEY_NAME and KEYRING_NAME

cypher_text = cloud_kms.Encrypt(clear_text, KEY_NAME, KEYRING_NAME)
clear_text = cloud_kms.Decrypt(cyper_text, KEY_NAME, KEYRING_NAME)
"""

import base64



from googleapiclient import discovery
import httplib2
from oauth2client import client

from google.appengine.api import app_identity

_LOCATION = 'global'
_client = None


def _BuildClient():
  discovery_uri = ('https://{api}.googleapis.com/$discovery/'
                   'google_rest_simple_uri?version={apiVersion}')
  creds = client.GoogleCredentials.get_application_default().create_scoped(
      ['https://www.googleapis.com/auth/cloudkms'])
  http_auth = creds.authorize(httplib2.Http())

  return discovery.build('cloudkms', 'v1', http=http_auth,
                         discoveryServiceUrl=discovery_uri)


def _GetAppId():
  return app_identity.get_application_id()


def _GetClient():
  global _client
  if _client:
    return _client

  _client = _BuildClient()

  return _client


def Encrypt(data, key_name, key_ring, key_location=_LOCATION):
  """Encrypts data and returns.

  Args:
    data: str, string to encrypt.
    key_name: str, Cloud KMS key to use for encryption.
    key_ring: str, key's key ring.
    key_location: str, Resource name for the location.
  Returns:
    unicode, encrypted data.
  Raises:
    ValueError: if key_name, key_ring or key_location is missing.
    googleapiclient.errors.Error: if server returned error.
  """
  if not key_name or not key_ring or not key_location:
    raise ValueError

  cloudkms = _GetClient()
  req = cloudkms.projects().locations().keyRings().cryptoKeys().encrypt(
      projectsId=_GetAppId(),
      locationsId=key_location,
      keyRingsId=key_ring,
      cryptoKeysId=key_name,
      body={'plaintext': base64.b64encode(data)})
  resp = req.execute()

  return resp['ciphertext']


def Decrypt(data, key_name, key_ring, key_location=_LOCATION):
  """Decrypts and returns encrypted_data.

  Args:
    data: str, data for decryption to encrypt.
    key_name: str, Cloud KMS key to use.
    key_ring: str, key's key ring.
    key_location: str, Resource name for the location.
  Returns:
    unicode, original string.
  Raises:
    ValueError: if key_name, key_ring or key_location is missing.
    googleapiclient.errors.Error: if server returned error.
  """
  if not key_name or not key_ring or not key_location:
    raise ValueError

  cloudkms = _GetClient()
  req = cloudkms.projects().locations().keyRings().cryptoKeys().decrypt(
      projectsId=_GetAppId(),
      locationsId=key_location,
      keyRingsId=key_ring,
      cryptoKeysId=key_name,
      body={'ciphertext': data})

  resp = req.execute()
  return base64.b64decode(resp['plaintext'])
