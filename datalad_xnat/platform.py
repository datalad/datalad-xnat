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

lgr = logging.getLogger('datalad.xnat.platform')


class _XNAT(object):
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
