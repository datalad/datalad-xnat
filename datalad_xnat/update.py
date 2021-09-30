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
import os
from pathlib import Path
from tempfile import mkstemp

from datalad.interface.base import Interface
from datalad.interface.utils import eval_results
from datalad.interface.base import build_doc
from datalad.interface.results import get_status_dict
from datalad.support.constraints import (
    EnsureNone,
    EnsureChoice,
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

from datalad.interface.common_opts import (
    jobs_opt,
)

from .platform import _XNAT


__docformat__ = 'restructuredtext'

lgr = logging.getLogger('datalad.xnat.update')


@build_doc
class Update(Interface):
    """Update files for a subject(s) of an XNAT project.

    This command expects an xnat-init initialized DataLad dataset. The dataset
    may or may not have existing content already.
    """

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            metavar='DATASET',
            doc="""specify the dataset to perform the update on""",
            constraints=EnsureDataset() | EnsureNone()
        ),
        ifexists=Parameter(
            args=("--ifexists",),
            doc="""Flag for addurls""",
            constraints=EnsureChoice(None, "overwrite", "skip")
        ),
        reckless=Parameter(
            args=("--reckless",),
            constraints=EnsureChoice(None, "fast",),
            metavar="fast",
            doc="""Update the files in a potentially unsafe way.
            Supported modes are:
            ["fast"]: No content verification or download. Will only register
            the urls.""",
        ),
        force=Parameter(
            args=("-f", "--force",),
            doc="""force (re-)building the addurl tables""",
            action='store_true'),
        jobs=jobs_opt,
        **_XNAT.cmd_params
    )

    @staticmethod
    @datasetmethod(name='xnat_update')
    @eval_results
    def __call__(project=None,
                 subject=None,
                 experiment=None,
                 collection=None,
                 credential=None,
                 force=False,
                 reckless=None,
                 ifexists=None,
                 jobs='auto',
                 dataset=None):


        ds = require_dataset(
            dataset, check_installed=True, purpose='update')

        xnat_cfg_name = ds.config.get('datalad.xnat.default-name', 'default')
        cfg_section = 'datalad.xnat.{}'.format(xnat_cfg_name)

        # TODO fail is there is no URL
        xnat_url = ds.config.get(f'{cfg_section}.url')
        # TODO fail without pathfmt
        pathfmt = ds.config.get(f'{cfg_section}.pathfmt')

        if project is None:
            project = ds.config.get(f'{cfg_section}.project')
        if subject is None:
            subject = ds.config.get(f'{cfg_section}.subject')
        if experiment is None:
            experiment = ds.config.get(f'{cfg_section}.experiment')
        if collection is None:
            collection = ds.config.get(f'{cfg_section}.collection', '').split()

        subjects = ensure_list(subject)

        # require a clean dataset
        if ds.repo.dirty:
            yield get_status_dict(
                'update',
                ds=ds,
                status='impossible',
                message=(
                    'Clean dataset required; use `datalad status` to inspect '
                    'unsaved changes'))
            return

        # prep for yield
        res = dict(
            action='xnat_update',
            path=ds.path,
            type='dataset',
            logger=lgr,
            refds=ds.path,
        )
        # obtain configured XNAT url and project name
        if not credential:
            credential = ds.config.get(
                '{}.credential-name'.format(cfg_section))

        platform = _XNAT(xnat_url, credential=credential)

        # parse and download one subject at a time
        # we could also make one big query
        if experiment is not None:
            # no need to query
            subjects = [None]
        elif subjects:
            # we can go with the subjects as-is
            pass
        elif project:
            # we have a project constraint, we can resolve subjects
            subjects = platform.get_subject_ids(project)
        else:
            # we have nothing to compartmentalize the query
            # go with a single big one
            subjects = [None]
        from datalad_xnat.parser import parse_xnat
        from unittest.mock import patch
        for sub in subjects:
            try:
                # all this tempfile madness is only needed because windows
                # cannot open the same file twice. shame!
                addurls_table, addurls_table_fname = mkstemp()
                addurls_table_fname = Path(addurls_table_fname)
                os.close(addurls_table)
                with open(
                        addurls_table_fname,
                        'w',
                        newline='',
                        encoding='utf-8') as addurls_table:
                    yield from parse_xnat(
                        addurls_table,
                        platform,
                        force=force,
                        project=project,
                        subject=sub,
                        experiment=experiment,
                        collections=ensure_list(collection)
                        if collection else None,
                    )

                # add file urls for subject
                lgr.info('Downloading files for subject %s', sub)
                # corresponds to the header field 'filename' in the csv table
                filename = '{filename}'
                filenameformat = f"{pathfmt}{filename}"
                # shoehorn essential info into the ENV to make it
                # accessible to the config procedure
                # TODO maybe alter the config procedure to pull this info
                # from a superdataset, if it finds the dataset at hand
                # unconfigured.
                env_prefix = f'DATALAD_XNAT_{xnat_cfg_name.upper()}'
                env = {
                    'DATALAD_XNAT_DEFAULT__NAME': xnat_cfg_name,
                    f'{env_prefix}_URL': platform.url,
                }
                if platform.credential_name != 'anonymous':
                    env[f'{env_prefix}_CREDENTIAL__NAME'] = \
                        platform.credential_name
                with patch.dict('os.environ', env):
                    ds.addurls(
                        str(addurls_table_fname), '{url}', filenameformat,
                        ifexists=ifexists,
                        fast=True if reckless == 'fast'
                        else False,
                        save=True,
                        jobs=jobs,
                        cfg_proc=None
                        if platform.credential_name == 'anonymous'
                        else 'xnat_dataset',
                        result_renderer='default')
            finally:
                if addurls_table_fname.exists():
                    addurls_table_fname.unlink()

        yield dict(
            res,
            status='ok'
        )
        return
