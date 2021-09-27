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
import csv

from datalad.interface.base import Interface
from datalad.interface.utils import eval_results
from datalad.interface.base import build_doc
from datalad.interface.results import get_status_dict
from datalad.support.constraints import (
    EnsureStr,
    EnsureNone,
    EnsureChoice,
)
from datalad.support.param import Parameter
from datalad.support.exceptions import CommandError
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
from urllib.parse import urlparse

from .platform import _XNAT

#import datalad.plugin.addurls

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
        subjects=Parameter(
            args=("-s", "--subjects"),
            nargs='+',
            doc="""Specify the subject(s) to downloaded associated files for.
            'list': list existing subjects,
            'all': download files for all existing subjects""",
        ),
        ifexists=Parameter(
            args=("--ifexists",),
            doc="""Flag for addurls""",
            constraints=EnsureChoice(None, "overwrite", "skip")
        ),
        force=Parameter(
            args=("-f", "--force",),
            doc="""force (re-)building the addurl tables""",
            action='store_true'),
        **_XNAT.cmd_params
    )

    @staticmethod
    @datasetmethod(name='xnat_update')
    @eval_results
    def __call__(subjects='list', credential=None, dataset=None, ifexists=None, force=False):

        ds = require_dataset(
            dataset, check_installed=True, purpose='update')

        subjects = ensure_list(subjects)

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

        platform = _XNAT(xnat_url, credential=credential)

        # provide subject list
        if 'list' in subjects:
            from datalad.ui import ui
            subs = platform.xn.select.project(xnat_project).subjects().get()
            ui.message(
                'The following subjects are available for XNAT '
                'project {}:'.format(xnat_project))
            for s in sorted(subs):
                ui.message(" {}".format(quote_cmdlinearg(s)))
            ui.message(
                'Specify a specific subject(s) or "all" to download associated '
                'files for.')
            return

        # query the specified subject(s) to make sure it exists and is accessible
        if 'all' not in subjects:
            from datalad.ui import ui
            subs = []
            for s in subjects:
                sub = platform.xn.select.project(xnat_project).subject(s)
                nexp = len(sub.experiments().get())
                if nexp > 0:
                    subs.append(s)
                else:
                    ui.message(
                        'Failed to obtain information on subject {} from XNAT '
                        'project {}:'.format(s, xnat_project))
                    return
        else:
            # if all, get list of all subjects
            subs = platform.xn.select.project(xnat_project).subjects().get()

        # parse and download one subject at a time
        from datalad_xnat.parser import parse_xnat
        addurl_dir = ds.pathobj / 'code' / 'addurl_files'
        for sub in subs:
            yield from parse_xnat(
                ds,
                sub=sub,
                force=force,
                xn=platform.xn,
                xnat_url=xnat_url,
                xnat_project=xnat_project,
            )

            # add file urls for subject
            lgr.info('Downloading files for subject %s', sub)
            table = f"{addurl_dir}/{sub}_table.csv"
            # this corresponds to the header field 'filename' in the csv table
            filename = '{filename}'
            filenameformat = f"{file_path}{filename}"
            ds.addurls(
                table, '{url}', filenameformat,
                ifexists=ifexists,
                save=False,
                cfg_proc=None if platform.cred['anonymous']
                else 'xnat_dataset',
                result_renderer='default',
            )

            ds.save(
                message=f"Update files for subject {sub}",
                recursive=True
            )

        lgr.info('Files were updated for the following subjects in XNAT project %s:', xnat_project)
        for s in sorted(subs):
            lgr.info(" {}".format(quote_cmdlinearg(s)))

        yield dict(
            res,
            status='ok'
        )
        return
