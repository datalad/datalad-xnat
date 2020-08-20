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
from datalad.interface.add_archive_content import AddArchiveContent
from datalad.support.constraints import (
    EnsureStr,
    EnsureNone,
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

__docformat__ = 'restructuredtext'

lgr = logging.getLogger('datalad.xnat.update')


@build_doc
class Update(Interface):
    """Lookup subjects for configured XNAT project and build csv tables for each
    subject that can be fed to datalad addurls.

    This command expects an xnat-init initialized DataLad dataset.
    """

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            metavar='DATASET',
            doc="""specify the dataset to perform the initialization on""",
            constraints=EnsureDataset() | EnsureNone()
        ),
        subject=Parameter(
            args=("-s", "--subject"),
            doc="""Specify the subject for whom to build a csv table.
            'list': list existing subjects,
            'all': create a table for all existing subjects""",
        ),
    )
    @staticmethod
    @datasetmethod(name='xnat_update')
    @eval_results
    def __call__(dataset=None, subject=None):
        from pyxnat import Interface as XNATInterface

        ds = require_dataset(
            dataset, check_installed=True, purpose='update')

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
        xnat_url = ds.config.obtain(
                '{}.url'.format(cfg_section),
                dialog_type='question',
                title='XNAT server address',
                text='Full URL of XNAT server (e.g. https://xnat.example.com:8443/xnat)',
                store=False,
                reload=False)

        xnat_project = ds.config.obtain(
                '{}.project'.format(cfg_section),
                dialog_type='question',
                title='XNAT project',
                text='Project on XNAT server',
                store=False,
                reload=False)

        # obtain user credentials
        cred = UserPassword(name=xnat_url, url=None)()
        xn = XNATInterface(server=xnat_url, **cred)

        if subject is None:
            from datalad.ui import ui
            # get list of all subjects
            subjects = xn.select.project(xnat_project).subjects().get()
            ui.message(
                    'No subject specified. The following subjects are available '
                    'for XNAT project {}:'.format(xnat_project))
            for s in sorted(subjects):
                ui.message(" {}".format(quote_cmdlinearg(s)))
            return

        # provide subject list
        if subject == 'list':
            from datalad.ui import ui
            subjects = xn.select.project(xnat_project).subjects().get()
            ui.message(
                    'The following subjects are available for XNAT '
                    'project {}:'.format(xnat_project))
            for s in sorted(subjects):
                ui.message(" {}".format(quote_cmdlinearg(s)))
            return

        # query the specified subject to make sure it exists and is accessible
        if subject != 'all':
            from datalad.ui import ui
            sub = xn.select.project(xnat_project).subject(subject)
            nexp = len(sub.experiments().get())
            if nexp > 0:
                subjects = [subject]
            else:
                ui.message(
                    'Failed to obtain information on subject {} from XNAT '
                    'project {}:'.format(subject, xnat_project))
                return
        else:
            # if all, get list of all subjects
            subjects = xn.select.project(xnat_project).subjects().get()

        # create csv table for each subject that contains subject info &
        # urls for each file
        table_header = ['subject','experiment','scan','resource','filename','url',]
        for subject in subjects:
            csv_path = f"addurl_files/{subject}_table.csv"
            sub_table = ds.pathobj / '{}'.format(csv_path)

            # check if table already exists
            if sub_table.exists():
                lgr.info('%s already exists', csv_path)
                #TODO: provide more info about existing file
                sub_table.unlink()

            sub_table.parent.mkdir(parents=True, exist_ok=True)

            # write subject info to file
            with open(sub_table, 'w') as outfile:
                fh = csv.writer(outfile, delimiter=',')
                fh.writerow(table_header)

                lgr.info('Querying info for subject %s', subject)
                xnsub = xn.select.project(xnat_project).subject(subject)
                for experiment in xnsub.experiments().get():
                    for scan in xnsub.experiment(experiment).scans().get():
                        for resource in xnsub.experiment(experiment).scan(scan).resources().get():
                            for filename in xnsub.experiment(experiment).scan(scan).resource(resource).files().get():
                                url = f"{xnat_url}/data/projects/{xnat_project}/subjects/{subject}/experiments/{experiment}/scans/{scan}/resources/{resource}/files/{filename}"
                                # create line for each file with necessary subject info
                                fh.writerow([subject, experiment, scan, resource, filename, url])

            # save current file
            ds.save(
                str(sub_table),
                to_git=True,
                message=f"Update XNAT info for subject {subject}"
            )

            lgr.info('%s created', csv_path)

        yield dict(
            res,
            status='ok'
        )
        return
