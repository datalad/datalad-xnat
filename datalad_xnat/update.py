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
        xnat_cfg_name = ds.config.get('datalad.xnat.default-name', 'default')
        cfg_section = 'datalad.xnat.{}'.format(xnat_cfg_name)
        xnat_url = ds.config.get('{}.url'.format(cfg_section))
        xnat_project = ds.config.get('{}.project'.format(cfg_section))
        file_path = ds.config.get('{}.path'.format(cfg_section))
        if not credential:
            credential = ds.config.get(
                '{}.credential-name'.format(cfg_section))

        platform = _XNAT(xnat_url, credential=credential)

        if not subjects:
            subjects = platform.get_subject_ids(xnat_project)

        # parse and download one subject at a time
        from datalad_xnat.parser import parse_xnat
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
                        project=xnat_project,
                        subject=sub,
                        experiment=experiment,
                        collections=ensure_list(collection)
                        if collection else None,
                    )

                # add file urls for subject
                lgr.info('Downloading files for subject %s', sub)
                # corresponds to the header field 'filename' in the csv table
                filename = '{filename}'
                filenameformat = f"{file_path}{filename}"
                ds.addurls(
                    str(addurls_table_fname), '{url}', filenameformat,
                    ifexists=ifexists,
                    fast=True if reckless == 'fast'
                    else False,
                    save=True,
                    jobs=jobs,
                    cfg_proc=None if platform.credential_name == 'anonymous'
                    else 'xnat_dataset',
                    result_renderer='default')
            finally:
                if addurls_table_fname.exists():
                    addurls_table_fname.unlink()

        lgr.info(
            'There were updates for the following subjects in project %s:',
            xnat_project)
        for s in sorted(subjects):
            lgr.info(" {}".format(quote_cmdlinearg(s)))

        yield dict(
            res,
            status='ok'
        )
        return
