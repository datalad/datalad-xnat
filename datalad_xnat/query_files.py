# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""

"""

import logging
from pathlib import PurePosixPath

from datalad.interface.base import Interface
from datalad.interface.utils import eval_results
from datalad.interface.base import build_doc

from datalad.support.param import Parameter

from datalad.distribution.dataset import (
    datasetmethod,
    EnsureDataset,
    require_dataset,
)
from datalad.utils import ensure_list
from .platform import _XNAT

__docformat__ = 'restructuredtext'

lgr = logging.getLogger('datalad.xnat.query')


# map which experiment properties to import into a file record under what
# name. all source name are lower-case
# these properties will overwrite any conflicting items in the file record!
_import_experiment_props = {
    'subject_id': 'subject_id',
    'id': 'experiment_id',
    'project': 'project_id',
    'uri': 'experiment_uri',
    'subject_label': 'subject_label',
}

_standardize_file_keys = {
    'size': 'byte-size',
    # this is an MD5sum, but is that always true?
    'digest': 'digest',
    'collection': 'collection',
    'name': 'name',
    'file_format': 'file_format',
    'file_content': 'file_content',
    'uri': 'uri',
}


@build_doc
class QueryFiles(Interface):
    """Query an XNAT server for projects, or an XNAT project for subjects

    Use this command to get a list of available projects at an XNAT instance
    for a given URL, or to get a list of subjects inside a specific project
    at the given XNAT instance.
    """

    _examples_ = [
        dict(
            text='Get a list of projects for a given XNAT instance:',
            code_cmd='datalad xnat-query http://central.xnat.org:8080',
            code_py='xnat_query("http://central.xnat.org:8080")'),
        dict(
            text='Get a list of subject for a given XNAT project:',
            code_cmd='datalad xnat-query http://central.xnat.org:8080 -p myproject',
            code_py='xnat_query("http://central.xnat.org:8080", project="myproject")'),
    ]

    _params_ = dict(
        url=Parameter(
            args=("url",),
            doc="""XNAT instance URL to query""",
        ),
        **_XNAT.cmd_params
    )

    @staticmethod
    @datasetmethod(name='xnat_query')
    @eval_results
    def __call__(url,
                 project=None,
                 experiment=None,
                 subject=None,
                 credential=None):

        platform = _XNAT(url, credential=credential)

        yield from query_files(
            platform,
            experiment=experiment,
            project=project,
            subject=subject,
        )


def query_files(platform, experiment=None, project=None, subject=None):
    # prep for yield
    res = dict(
        action='xnat_query',
        logger=lgr
    )

    if experiment and (project or subject):
        lgr.warning(
            'experiment given, will ignore project and subject '
            'specifications')
    experiments = {}
    if experiment:
        # inject experiment record placeholders, to trigger a later
        # query
        for er in ensure_list(experiment):
            experiments[er] = None
    else:
        # query for experiments, based potential project and subject
        # constraints
        for er in platform.get_experiments(
                project=project,
                subject=subject):
            # normalize keys
            er = {k.lower(): v for k, v in er.items()}
            experiments[er['id']] = er

    for eid, er in experiments.items():
        if not er:
            er = {
                k.lower(): v
                for k, v in platform.get_experiment(eid).items()
            }

        for fr in platform.get_files(eid):
            fr = {
                _standardize_file_keys[k.lower()]: v
                for k, v in fr.items()
                if k.lower() in _standardize_file_keys
            }
            # spot check digest
            digest = fr.pop('digest', '')
            if len(digest) == 32:
                fr['digest-md5'] = digest
            else:
                lgr.debug('Unrecognized digest of length %i ignored',
                          len(digest))
            # figure our scan ID from URI
            path = PurePosixPath(fr['uri'])
            # API is /data/experiments/ID/scans/ID/resources/ID/files/NAME
            fr['scan_id'] = path.parts[5]
            # we need a file extension for conveniently building E-keys
            # for git-annex
            # we cannot use '.suffixes', because an entire DICOM filename
            # is considered a suffix ;-)
            fr['name_suffix'] = ''.join(PurePosixPath(fr['name']).suffix)
            # inject a full URL for convenience too
            fr['url'] = f'{platform.url}{fr["uri"]}'
            for ik, ek in _import_experiment_props.items():
                if ik in er:
                    fr[ek] = er[ik]
            yield dict(
                res,
                status='ok',
                type='file',
                # give artificial internal XNAT path, matches API,
                # improves comprehension
                path=f"{fr['experiment_id']}/{fr['scan_id']}/{fr['name']}",
                # include collection info (i.e. resource)
                message=fr.get('collection'),
                **fr
            )
