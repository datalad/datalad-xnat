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
import requests
from urllib.parse import (
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
    # URL must not have a leading slash
    api_endpoints = dict(
        session_token='data/JSESSION',
        projects='data/projects?format=json',
        subjects='data/projects/{project}/subjects?format=json',
        experiments='data/projects/{project}/subjects/{subject}/experiments?format=json',
        scans='data/experiments/{experiment}/scans?format=json',
        files='data/experiments/{experiment}/scans/{scan}/files?format=json',
    )

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
        # all URL joining operations require NO trailing slash of the base URL
        self.url = url.rstrip('/')

        session = requests.Session()
        if credential is None:
            credential = urlparse(url).netloc

        if credential == 'anonymous':
            auth = None
        else:
            try:
                auth = UserPassword(
                    credential,
                    url=f'{url}/app/template/Register.vm',
                )()
            except Exception as e:
                lgr.debug('Credential retrieval failed: %s', e)
                lgr.warning(
                    'Cannot determine user/password for %s', credential)
                raise ValueError(
                    f'Authorization required for {self.fullname}, '
                    f'cannot find token for a credential {credential}.') from e

            session.auth = (auth['user'], auth['password'])

        # now check of auth works (if any is needed)
        # TODO check that we have anonymous OR user/pass
        try:
            session.post(self._get_api('session_token')).raise_for_status()
        except Exception as e:
            # TODO this exception as enough info to actually do meaningful
            # error handling
            raise RuntimeError(
                'Failed to access the XNAT server. Full error:\n%s', e) from e

        self._session = session
        self._credential_name = credential

    @property
    def credential_name(self):
        return self._credential_name

    @property
    def authenticated_user(self):
        return self._session.auth[0] if self._session else None

    def get_projects(self):
        """Returns a list with project identifiers"""
        return self._unwrap_ids(self._session.get(
            self._get_api('projects')))

    def get_subjects(self, project):
        """Return a list of subject IDs available in a project"""
        return self._unwrap_ids(self._session.get(
            self._get_api('subjects', project=project)))

    def get_nsubjs(self, project):
        """Return the number of subjects available in a project"""
        return len(self.get_subjects(project))

    def get_experiments(self, project, subject):
        """Return a list of experiment IDs available for a project's subject"""
        return self._unwrap_ids(self._session.get(
            self._get_api('experiments',
                          project=project,
                          subject=subject)))

    def get_scans(self, experiment):
        """Return a list of scan IDs available for an experiment"""
        return self._unwrap_ids(self._session.get(
            self._get_api('scans', experiment=experiment)))

    def get_files(self, experiment, scan):
        """Return a list of file records for a scan in an experiment"""
        return self._unwrap(self._session.get(
            self._get_api('files', experiment=experiment, scan=scan)))

    def _get_api(self, id, **kwargs):
        ep = self.api_endpoints[id]
        if kwargs:
            ep = ep.format(**kwargs)
        return f'{self.url}/{ep}'

    def _unwrap(self, response):
        return response.json().get('ResultSet', {}).get('Result')

    def _unwrap_ids(self, response):
        unwrapped = self._unwrap(response)
        # do a little dance to figure out what the ID key is
        # normal XNAT is 'ID', but connectomeDB uses 'id'
        # TODO is there a way to ask XNAT what it would be
        # maybe query the schema?
        id_attr = 'ID' if unwrapped and 'ID' in unwrapped[0] else 'id'
        return [r[id_attr] for r in unwrapped]
