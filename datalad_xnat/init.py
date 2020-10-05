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
from datalad.support.constraints import (
    EnsureStr,
    EnsureNone,
)
from datalad.support.param import Parameter
from datalad.utils import (
    ensure_list,
    quote_cmdlinearg,
)

from datalad.distribution.dataset import (
    datasetmethod,
    EnsureDataset,
    require_dataset,
)
from datalad.downloaders.credentials import UserPassword


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
        force=Parameter(
            args=("-f", "--force",),
            doc="""force (re-)initialization""",
            action='store_true'),
    )
    @staticmethod
    @datasetmethod(name='xnat_init')
    @eval_results
    def __call__(url, project=None, force=False, dataset=None):
        from pyxnat import Interface as XNATInterface

        ds = require_dataset(
            dataset, check_installed=True, purpose='initialization')

        config = ds.config

        # prep for yield
        res = dict(
            action='xnat_init',
            path=ds.path,
            type='dataset',
            logger=lgr,
            refds=ds.path,
        )

        # obtain user credentials, use provided URL as identifier
        # given we don't have more knowledge than the user, do not
        # give a `url` to provide hints on how to obtain credentials
        cred = UserPassword(name=url, url=None)()

        xn = XNATInterface(server=url, **cred)

        # now we make a simple request to obtain the server version
        # we don't care much, but if the URL or the credentials are wrong
        # we will not get to see one
        try:
            xnat_version = xn.version()
            lgr.debug("XNAT server version is %s", xnat_version)
        except Exception as e:
            yield dict(
                res,
                status='error',
                message=(
                    'Failed to access the XNAT server. Full error:\n%s',
                    e),
            )
            return

        if project is None:
            from datalad.ui import ui
            projects = xn.select.projects().get()
            ui.message(
                'No project name specified. The following projects are '
                'available on {} for user {}:'.format(url, cred['user']))
            for p in sorted(projects):
                # list and prep for C&P
                # TODO multi-column formatting?
                ui.message("  {}".format(quote_cmdlinearg(p)))
            return

        # query the specified project to make sure it exists and is accessible
        proj = xn.select.project(project)

        try:
            nsubj = len(proj.subjects().get())
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

        # put essential configuration into the dataset
        config.set('datalad.xnat.default.url', url, where='dataset', reload=False)
        config.set('datalad.xnat.default.project', project, where='dataset')

        ds.save(
            path=ds.pathobj / '.datalad' / 'config',
            to_git=True,
            message="Configure default XNAT url and project",
        )

        # Configure XNAT access authentication
        ds.run_procedure(spec='cfg_xnat_dataset')

        yield dict(
            res,
            status='ok',
        )
        return
