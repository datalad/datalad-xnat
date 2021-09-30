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
from datalad.interface.results import get_status_dict
from datalad.support.constraints import (
    EnsureNone,
)

from datalad.support.exceptions import CapturedException
from datalad.support.param import Parameter
from datalad.utils import (
    quote_cmdlinearg,
)
from datalad.distribution.dataset import (
    datasetmethod,
    EnsureDataset,
    require_dataset,
)
from .platform import (
    _XNAT,
    XNATRequestError
)

__docformat__ = 'restructuredtext'

lgr = logging.getLogger('datalad.xnat.init')


@build_doc
class Init(Interface):
    """Initialize an existing dataset to track an XNAT project
    """

    _examples_ = [
        dict(
            text='Initialize a dataset in the current directory',
            code_cmd='datalad xnat-init http://central.xnat.org:8080',
            code_py='xnat_init("http://central.xnat.org:8080")'),
        dict(
            text='Initialize with anonymous access (no credentials used)',
            code_cmd=('datalad xnat-init https://central.xnat.org '
                      '--credential anonymous'),
            code_py=('xnat_init("https://central.xnat.org", '
                     'credential="anonymous")')),
        dict(
            text='Use credentials previously stored as <NAME>',
            code_cmd=('datalad xnat-init https://central.xnat.org '
                      '--credential <NAME>'),
            code_py=('xnat_init("https://central.xnat.org", '
                     'credential="<NAME>")')),
        dict(
            text='Track a specific XNAT project, without credentials',
            code_cmd=('datalad xnat-init https://central.xnat.org '
                      '--project Sample_DICOM --credential anonymous'),
            code_py=('xnat_init("https://central.xnat.org", '
                     'project="Sample_DICOM", credential="anonymous")')),
    ]

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            metavar='DATASET',
            doc="""specify the dataset to perform the initialization on""",
            constraints=EnsureDataset() | EnsureNone()),
        url=Parameter(
            args=("url",),
            doc="""XNAT instance URL""",
        ),
        project=Parameter(
            args=("-p", "--project",),
            doc="""name of an XNAT project to track""",
        ),
        path=Parameter(
            args=("-O", "--path",),
            doc="""Specify the directory structure for the downloaded files, and
            if/where a subdataset should be created.
            To include the subject, session, or scan values, use the following
            format: {subject}/{session}/{scan}/
            To insert a subdataset at a specific directory level use '//':
            {subject}/{session}//{scan}/""",
        ),
        force=Parameter(
            args=("-f", "--force",),
            doc="""force (re-)initialization""",
            action='store_true'),
        **_XNAT.cmd_params
    )

    @staticmethod
    @datasetmethod(name='xnat_init')
    @eval_results
    def __call__(url,
                 path="{subject}/{session}/{scan}/",
                 project=None,
                 force=False,
                 credential=None,
                 dataset=None):

        ds = require_dataset(
            dataset, check_installed=True, purpose='initialization')

        # TODO needs a better solution, with_pathsep adds a platform pathsep
        # and ruins everything on windows
        #path = with_pathsep(path)

        # prep for yield
        res = dict(
            action='xnat_init',
            path=ds.path,
            type='dataset',
            logger=lgr,
            refds=ds.path,
        )

        try:
            platform = _XNAT(url, credential=credential)
        except XNATRequestError as e:
            ce = CapturedException(e)
            yield get_status_dict(
                status='error',
                message=ce.message,
                exception=ce,
                **res,
            )
            return
        except Exception as e:
            ce = CapturedException(e)
            yield get_status_dict(
                status='error',
                message=('During authentication the XNAT server sent %s', ce),
                exception=ce,
                **res,
            )
            return

        if project is None:
            from datalad.ui import ui
            lgr.info('Querying %s for projects available to user %s', url,
                     'anonymous' if platform.credential_name == 'anonymous'
                     else platform.authenticated_user)
            projects = platform.get_project_ids()
            ui.message(
                'No project name specified. The following projects are '
                'available on {} for user {}:'.format(
                    url,
                    'anonymous' if platform.credential_name == 'anonymous'
                    else platform.authenticated_user))
            for p in sorted(projects):
                # list and prep for C&P
                # TODO multi-column formatting?
                ui.message("  {}".format(quote_cmdlinearg(p)))
            return

        # query the specified project to make sure it exists and is accessible
        try:
            # TODO for big projects this may not be the cheapest possible query
            # that ensures existence of the project
            nsubj = platform.get_nsubjs(project)
        except Exception as e:
            yield dict(
                res,
                status='error',
                message=(
                    'Failed to obtain information on project %s from XNAT. '
                    'Full error:\n%s',
                    project, e),
            )
            return

        lgr.info('XNAT reports %i subjects currently on-record for project %s',
                 nsubj, project)

        # check if dataset already initialized
        auth_dir = ds.pathobj / '.datalad' / 'providers'
        if auth_dir.exists() and not force:
            yield dict(
                res,
                status='error',
                message='Dataset found already initialized, '
                        'use `force` to reinitialize',
            )
            return

        _cfg_dataset(ds, url, project, path, platform.credential_name)

        if not platform.credential_name == 'anonymous':
            # Configure XNAT access authentication
            ds.run_procedure(spec='cfg_xnat_dataset')

        yield dict(
            res,
            status='ok',
        )
        return


def _cfg_dataset(ds, url, project, path_spec, credential_name):
    config = ds.config
    # put essential configuration into the dataset
    # TODO https://github.com/datalad/datalad-xnat/issues/42
    for k, v in (('url', url),
                 ('project', project),
                 ('path', path_spec),
                 ('credential-name', credential_name)):
        config.set(
            f'datalad.xnat.default.{k}',
            v,
            where='dataset',
            reload=False)

    ds.save(
        path=ds.pathobj / '.datalad' / 'config',
        to_git=True,
        message="Configure default XNAT url and project",
    )
    config.reload()
