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
from datalad.ui import ui
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
        pathfmt=Parameter(
            args=("-F", "--pathfmt",),
            doc="""Specify the directory structure for the downloaded files, and
            if/where a subdataset should be created. The format string must use
            POSIX notation and must end with a slash ('/').
            To include the subject, session, or scan values, use the following
            format: {subject}/{session}/{scan}/
            To insert a subdataset at a specific directory level use '//':
            {subject}/{session}//{scan}/""",
        ),
        force=Parameter(
            args=("-f", "--force",),
            doc="""force (re-)initialization""",
            action='store_true'),
        interactive=Parameter(
            args=("--interactive",),
            doc="""enables interactive configuration based on XNAT queries.
            Default: enabled in interactive sessions.""",
            action='store_true'),
        **_XNAT.cmd_params
    )

    @staticmethod
    @datasetmethod(name='xnat_init')
    @eval_results
    def __call__(url,
                 pathfmt="{subject}/{session}/{scan}/",
                 project=None,
                 subject=None,
                 experiment=None,
                 collection=None,
                 credential=None,
                 force=False,
                 interactive=None,
                 dataset=None):

        if not pathfmt[-1] == '/':
            raise ValueError(
                'Path format specification must end with a slash character')

        if interactive is None:
            interactive = ui.is_interactive

        ds = require_dataset(
            dataset, check_installed=True, purpose='initialization')

        # prep for yield
        res = dict(
            action='xnat_init',
            path=ds.path,
            type='dataset',
            logger=lgr,
            refds=ds.path,
        )

        # check if dataset already initialized
        if not force and 'datalad.xnat.default.url' in ds.config:
            yield dict(
                res,
                status='error',
                message='Dataset found already initialized, '
                        'use `force` to reinitialize',
            )
            return

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

        if interactive:
            # makes queries and let a user pick values
            if project is None:
                pass
            if subject is None:
                pass
            if experiment is None:
                pass
            if collection is None:
                pass
        # at this point, any None value of project, subject, experiment,
        # collection means: do not limit -- take all

        _cfg_dataset(
            ds,
            url,
            project,
            subject,
            experiment,
            collection,
            pathfmt,
            platform.credential_name,
        )

        if not platform.credential_name == 'anonymous':
            # Configure XNAT access authentication
            ds.run_procedure(spec='cfg_xnat_dataset')

        yield dict(
            res,
            status='ok',
        )
        return


def _cfg_dataset(ds, url, project, subject, experiment, collection,
                 pathfmt, credential_name):
    config = ds.config
    # put essential configuration into the dataset
    # TODO https://github.com/datalad/datalad-xnat/issues/42
    for k, v in (('url', url),
                 ('project', project),
                 ('subject', subject),
                 ('experiment', experiment),
                 ('collection', collection),
                 ('pathfmt', pathfmt),
                 ('credential-name', credential_name)):
        cfgvar = f'datalad.xnat.default.{k}'
        if v is None:
            if cfgvar in config:
                config.unset(cfgvar, where='dataset', reload=False)
        else:
            config.set(
                cfgvar,
                ' '.join(v) if isinstance(v, list) else v,
                where='dataset',
                reload=False)

    ds.save(
        path=ds.pathobj / '.datalad' / 'config',
        to_git=True,
        message="Configure default XNAT url and project",
    )
    config.reload()
