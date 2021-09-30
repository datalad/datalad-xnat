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

from datalad_xnat.query_files import query_files

lgr = logging.getLogger('datalad.xnat.parse')


def parse_xnat(ds, sub, force, platform, xnat_project):
    """Lookup specified subject for configured XNAT project and build csv table.

    Parameters
    ----------
    ds: Dataset
    sub: str
        The subject to build a csv table for.
    force: str
        Re-build csv table if it already exists.
    platform: str
        XNAT instance
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
    table_header = ['subject', 'session', 'scan', 'filename', 'url']
    sub_table = ds.pathobj / 'code' / 'addurl_files' / f'{sub}_table.csv'

    # check if table already exists
    if sub_table.exists() and not force:
        lgr.info(
            '%s already exists. To query latest subject info, use `force`.',
            sub_table)
        return
        #TODO: provide more info about existing file
    elif sub_table.exists() and force:
        sub_table.unlink()

    sub_table.parent.mkdir(parents=True, exist_ok=True)

    # write subject info to file
    with open(sub_table, 'w', newline='', encoding='utf-8') as outfile:
        fh = csv.writer(outfile, delimiter=',')
        fh.writerow(table_header)
        lgr.info('Querying info for subject %s', sub)
        for fr in query_files(platform, project=xnat_project, subject=sub):
            # TODO the file size is at file_rec['Size'], could be used
            # for progress reporting, maybe
            # create line for each file with necessary subject info
            fh.writerow([
                fr['subject_id'],
                fr['experiment_id'],
                fr['scan_id'],
                fr['name'],
                fr['url'],
            ])

    ds.save(
        path=sub_table,
        message=f"Add file url table for {sub}",
        to_git=True
    )

    yield dict(
        res,
        status='ok',
    )
