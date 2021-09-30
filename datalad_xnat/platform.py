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

from http import HTTPStatus
from requests import (
    HTTPError,
    Session,
)
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


# lookup error description based on HTTP error code
http_error_lookup = {i.value: i.phrase for i in HTTPStatus}


class XNATRequestError(Exception):
    """A request to an XNAT server resulted in an error

    This exists to explicitly distinguish an exception raised from within this
    package from a generic one bubbling up, in order to be able to handle them
    differently.
    """
    pass


class _XNAT(object):
    # URL must not have a leading slash
    api_endpoints = dict(
        session_token='data/JSESSION',
        projects='data/projects?format=json',
        subjects='data/projects/{project}/subjects?format=json',
        experiment='data/experiments/{experiment}?format=json',
        experiments='data/experiments?format=json',
        scans='data/experiments/{experiment}/scans?format=json',
        files='data/experiments/{experiment}/scans/ALL/files?format=json',
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
        project=Parameter(
            args=("-p", "--project",),
            metavar='ID',
            doc="""accession ID of a single XNAT project to track""",
        ),
        subject=Parameter(
            args=("-s", "--subject",),
            metavar='ID',
            doc="""accession ID of a single subject to track""",
        ),
        experiment=Parameter(
            args=("-e", "--experiment",),
            metavar='ID',
            doc="""accession ID of a single experiment to track""",
        ),
        collection=Parameter(
            args=("-c", "--collection",),
            metavar='LABEL',
            action='append',
            doc="""limit updates to a specific collection/resource.
            [CMD: Can be given multiple times CMD][PY: Multiple collections
            can be specified as a list PY]""",
        ),
    )

    def __init__(self, url, credential):
        # all URL joining operations require NO trailing slash of the base URL
        self.url = url.rstrip('/')

        session = Session()
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
                    f'Authorization required for {self.url}, '
                    f'cannot find token for a credential {credential}.') from e

            session.auth = (auth['user'], auth['password'])

        self._session = session
        # now check if auth works (if any is needed)
        # TODO check that we have anonymous OR user/pass
        self._wrapped_post(self._get_api('session_token'))
        self._credential_name = credential

    def _wrapped_request(self, method, *args, **kwargs):
        """Helper for `_wrapped_get` and `_wrapped_post`"""

        if method not in ['GET', 'POST']:
            raise ValueError("method parameter can either be 'GET' or 'POST'.")

        req = self._session.get if method == 'GET' else self._session.post

        try:
            lgr.debug('%s: %s, %s', method, args, kwargs)
            response = req(*args, **kwargs)
            response.raise_for_status()
            return response
        except HTTPError as exc:
            reason = exc.response.reason or \
                     http_error_lookup[exc.response.status_code]
            raise XNATRequestError("Request to XNAT server failed: %s"
                                   % reason) from exc

    def _wrapped_get(self, *args, **kwargs):
        """Wraps `self._session.get` for error handling.

        Parameters
        ----------
        args:
        kwargs:
          passed on to self._session.get

        Returns
        -------
        requests.Response

        Raises
        ------
        XNATRequestError
        """

        return self._wrapped_request('GET', *args, **kwargs)

    def _wrapped_post(self, *args, **kwargs):
        """Wraps `self._session.post` for error handling.

        Parameters
        ----------
        args:
        kwargs:
          passed on to self._session.post

        Returns
        -------
        requests.Response

        Raises
        ------
        XNATRequestError
        """

        return self._wrapped_request('POST', *args, **kwargs)

    @property
    def credential_name(self):
        return self._credential_name

    @property
    def authenticated_user(self):
        return self._session.auth[0] if self._session else None

    def get_projects(self):
        """Returns a list with project records"""
        return self._unwrap(self._wrapped_get(self._get_api('projects')))

    def get_project_ids(self):
        """Returns a list with project identifiers"""
        return self._unwrap_ids(self.get_projects())

    def get_subject_ids(self, project):
        """Return a list of subject IDs available in a project"""
        return self._unwrap_ids(self._unwrap(self._wrapped_get(
            self._get_api('subjects', project=project))))

    def get_nsubjs(self, project):
        """Return the number of subjects available in a project"""
        return len(self.get_subject_ids(project))

    def get_experiment(self, experiment):
        """Return an experiment record"""
        url = self._get_api('experiment', experiment=experiment)
        items = self._wrapped_get(url).json().get('items', [])
        if not items:
            return
        if len(items) > 1:
            raise ValueError('Non-unique experiment identifier')
        return items[0]['data_fields']

    def get_experiments(self, project=None, subject=None):
        """Return a list of experiment records for a project's subject"""
        url = self._get_api('experiments')
        # optionally constrain the query
        if project:
            url += f'&project={project}'
        if subject:
            url += f'&subject_ID={subject}'
        return self._unwrap(self._wrapped_get(url))

    def get_experiment_ids(self, project=None, subject=None):
        """Return a list of experiment IDs available for a project's subject"""
        return self._unwrap_ids(self.get_experiments(project, subject))

    def get_scan_ids(self, experiment):
        """Return a list of scan IDs available for an experiment"""
        return self._unwrap_ids(self._unwrap(self._wrapped_get(
            self._get_api('scans', experiment=experiment))))

    def get_files(self, experiment):
        """Return a list of file records for a scan in an experiment"""
        return self._unwrap(self._wrapped_get(
            self._get_api('files', experiment=experiment)))

    def _get_api(self, id, **kwargs):
        ep = self.api_endpoints[id]
        if kwargs:
            ep = ep.format(**kwargs)
        return f'{self.url}/{ep}'

    def _unwrap(self, response):
        return response.json().get('ResultSet', {}).get('Result')

    def _unwrap_ids(self, results):
        # do a little dance to figure out what the ID key is
        # normal XNAT is 'ID', but connectomeDB uses 'id'
        # TODO is there a way to ask XNAT what it would be
        # maybe query the schema?
        id_attr = 'ID' if results and 'ID' in results[0] else 'id'
        return [r[id_attr] for r in results]
