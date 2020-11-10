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
from datalad.utils import quote_cmdlinearg

lgr = logging.getLogger('datalad.xnat.parse')


def parse_xnat(ds, sub, force, xn, xnat_url, xnat_project):
    """Lookup specified subject for configured XNAT project and build csv table.

    Parameters
    ----------
    ds: Dataset
    sub: str
        The subject to build a csv table for.
    force: str
        Re-build csv table if it already exists.
    xn: str
        XNAT instance
    xnat_url: str
    xnat_project: str
    """

    # prep for yield
    res = dict(
        action='xnat_parse',
        type='file',
        logger=lgr,
        refds=ds.path,
    )

    # create csv table containing subject info & file urls
    table_header = ['subject', 'session', 'scan', 'resource', 'filename', 'url']
    csv_path = f"code/addurl_files/{sub}_table.csv"
    sub_table = ds.pathobj / '{}'.format(csv_path)

    # check if table already exists
    if sub_table.exists() and not force:
        lgr.info('%s already exists. To query latest subject info, use `force`.', csv_path)
        return
        #TODO: provide more info about existing file
    elif sub_table.exists() and force:
        sub_table.unlink()

    sub_table.parent.mkdir(parents=True, exist_ok=True)

    # write subject info to file
    with open(sub_table, 'w') as outfile:
        fh = csv.writer(outfile, delimiter=',')
        fh.writerow(table_header)

        lgr.info('Querying info for subject %s', sub)
        xnsub = xn.select.project(xnat_project).subject(sub)
        for experiment in xnsub.experiments().get():
            for scan in xnsub.experiment(experiment).scans().get():
                for resource in xnsub.experiment(experiment).scan(scan).resources().get():
                    for filename in xnsub.experiment(experiment).scan(scan).resource(resource).files().get():
                        url = f"{xnat_url}/data/projects/{xnat_project}/subjects/{sub}/experiments/{experiment}/scans/{scan}/resources/{resource}/files/{filename}"
                        # create line for each file with necessary subject info
                        fh.writerow([sub, experiment, scan, resource, filename, url])
    yield dict(
        res,
        status='ok',
    )
