# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Platform abstraction for XNAT instances
"""

import logging
from urllib.parse import (
    urljoin,
    urlparse,
)

from datalad.downloaders.credentials import UserPassword
from datalad.support.constraints import (
    EnsureNone,
    EnsureStr,
)
from datalad.support.param import Parameter

lgr = logging.getLogger('datalad.xnat.platform')


class _XNAT(object):

    cmd_params = dict(
        credential=Parameter(
            args=('--credential',),
            constraints=EnsureStr() | EnsureNone(),
            metavar='NAME',
            doc="""name of the credential providing a user/password combination
            to be used for authentication. The special value 'anonymous' will
            cause no credentials to be used, and all XNAT requests to be
            performed anonymously. The credential can be supplied via
            configuration settings 'datalad.credential.<name>.{user|password}',
            or environment variables DATALAD_CREDENTIAL_<NAME>_{USER|PASSWORD},
            or will be queried from the active credential store using the
            provided name. If none is provided, the host-part of the XNAT URL
            is used as a name (e.g. 'https://central.xnat.org' ->
            'central.xnat.org')"""),
    )

    def __init__(self, url, credential):
        from pyxnat import Interface as XNATInterface

        if credential is None:
            credential = urlparse(url).netloc

        if credential == 'anonymous':
            cred = dict(anonymous=True, user=None, password=None)
        else:
            try:
                auth = UserPassword(
                    credential,
                    url=urljoin(url, 'app/template/Register.vm'),
                )()
            except Exception as e:
                lgr.debug('Credential retrieval failed: %s', e)
                lgr.warning(
                    'Cannot determine user/password for %s', credential)
                raise ValueError(
                    f'Authorization required for {self.fullname}, '
                    f'cannot find token for a credential {credential}.') from e

            cred = dict(anonymous=False,
                        user=auth['user'] or None,
                        password=auth['password'] or None)

        # TODO check that we have anonymous OR user/pass
        xn = XNATInterface(server=url, **cred)

        # now we make a simple request to obtain the server version
        # we don't care much, but if the URL or the credentials are wrong
        # we will not get to see one
        try:
            xnat_version = xn.version()
            lgr.debug("XNAT server version is %s", xnat_version)
        except Exception as e:
            # TODO this exception as enough info to actually do meaningful
            # error handling
            raise RuntimeError(
                'Failed to access the XNAT server. Full error:\n%s', e) from e

        # TODO make private
        self.xn = xn
        self.cred = cred
