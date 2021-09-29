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

from datalad.interface.base import Interface
from datalad.interface.utils import eval_results
from datalad.interface.base import build_doc

from datalad.support.param import Parameter

from datalad.distribution.dataset import (
    datasetmethod,
    EnsureDataset,
    require_dataset,
)
from .platform import _XNAT

__docformat__ = 'restructuredtext'

lgr = logging.getLogger('datalad.xnat.init')

@build_doc
class Query(Interface):
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
        project=Parameter(
            args=("-p", "--project",),
            doc="""name of an XNAT project to query""",
        ),
        **_XNAT.cmd_params
    )

    @staticmethod
    @datasetmethod(name='xnat_query')
    @eval_results
    def __call__(url,
                 project=None,
                 credential=None):

        platform = _XNAT(url, credential=credential)
        # prep for yield
        res = dict(
            action='xnat_query',
            type='directory',
            logger=lgr
        )

        if project is None:
            # query the platform for all available projects and report them.
            projects = platform.get_projects()
            yield dict(status='ok',
                       message=projects,
                       path=url,
                       **res)

        else:
            # report available subjects for the project
            subjects = platform.get_subjects(project)
            yield dict(action='xnat-query',
                       status='ok',
                       message=subjects,
                       path=url,
                       **res)
