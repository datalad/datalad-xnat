"""
Configure a DataLad dataset with XNAT server authentication.

Multiple XNAT servers can be configured (one at at time). The dataset procedure
take all necessary information from the DataLad configuration. The following
variables are supported (default in parentheses, if there is any):

- datalad.xnat.default-name (default)

  The NAME of an XNAT instance, only used as a label for configuration lookup.

- datalad.xnat.NAME.url

  URL of the respective XNAT server instance. This is typically the URL of
  the main login page. This configuration is mandatory. Its value will be
  asked for interactively, if no configuration is found.

- datalad.xnat.NAME.authentication_type (http_basic_auth)

  Any DataLad-supported authentication type, like 'http_digest_auth'.

- datalad.xnat.NAME.credential_type (user_password)

  Any DataLad-supported credential type, like 'token'.

How to run:

In the simplest case the procedure is executed with no prior configuration.
It will interactively ask for the XNAT server URL and configure user/password
based authentication via HTTP basic auth, a common XNAT setup.

In unattended scenarios, the server URL can be provided via configuration
variable DATALAD_XNAT_DEFAULT_URL.

When (mutiple) XNAT server configuration are available, a particular one can be
selected via the DATALAD_XNAT_DEFAULT__NAME environment variable. For example,
the following configuration can be selected and applied by setting
DATALAD_XNAT_DEFAULT__NAME=myxnat

  datalad.xnat.myxnat.url=https://xnat.example.com
  datalad.xnat.myxnat.authentication-type=bearer_token
  datalad.xnat.myxnat.credentialr-type=token
"""

import sys

from datalad.api import Dataset
from urllib.parse import urlparse
from datalad.support.annexrepo import AnnexRepo
from datalad.consts import DATALAD_SPECIAL_REMOTE
from datalad.support.exceptions import (RemoteNotAvailableError)

ds = Dataset(sys.argv[1])

xnat_cfg_name = ds.config.get('datalad.xnat.default-name', 'default')
cfg_section = 'datalad.xnat.{}'.format(xnat_cfg_name)
xnat_url = ds.config.obtain(
    '{}.url'.format(cfg_section),
    dialog_type='question',
    title='XNAT server address',
    text='Full URL of XNAT server (e.g. https://xnat.example.com:8443/xnat)',
    store=False,
    reload=False)

parsed_url = urlparse(xnat_url)

auth_cfg = """\
[provider:xnat-{name}]
url_re = {url}/.*
credential = {credential_name}
authentication_type = {auth_type}

[credential:{credential_name}]
type = {cred_type}
""".format(
    name=xnat_cfg_name,
    # strip /, because it is in the template
    url=xnat_url.rstrip('/'),
    # use a simplified/stripped URL as identifier for the credential cfg
    credential_name=ds.config.obtain('{}.credential-name'.format(cfg_section)),
    auth_type=ds.config.obtain(
        '{}.authentication-type'.format(cfg_section),
        'http_basic_auth'),
    cred_type=ds.config.obtain(
        '{}.credential-type'.format(cfg_section),
        'user_password'),
)

# place in a file that contains the config name
auth_file = ds.pathobj / '.datalad' / 'providers' / 'xnat-{}.cfg'.format(
    xnat_cfg_name)

# don't stress with prev variants, all in git anyways
if auth_file.exists():
    auth_file.unlink()
auth_file.parent.mkdir(parents=True, exist_ok=True)

# write and save file to git
auth_file.write_text(auth_cfg)
ds.save(
    str(auth_file),
    to_git=True,
    message="Configure XNAT access authentication",
)

# enable datalad special remote
annex = AnnexRepo(ds.path)
try:
    annex.is_special_annex_remote(DATALAD_SPECIAL_REMOTE)
except RemoteNotAvailableError:
    annex.init_remote(DATALAD_SPECIAL_REMOTE,
        ['encryption=none', 'type=external', 'externaltype=%s' % DATALAD_SPECIAL_REMOTE,
            'autoenable=true'])
