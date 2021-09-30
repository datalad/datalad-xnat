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


def parse_xnat(outfile, sub, force, platform, xnat_project):
    """Lookup specified subject for configured XNAT project and build csv table.

    Parameters
    ----------
    outfile: file-like
        Writable file descriptor.
    sub: str
        The subject to build a csv table for.
    force: str
        Re-build csv table if it already exists.
    platform: str
        XNAT instance
    xnat_project: str
    """
    # create csv table containing subject info & file urls
    table_header = ['subject', 'session', 'scan', 'filename', 'url']

    # write subject info to file
    fh = csv.writer(outfile, delimiter=',')
    fh.writerow(table_header)
    lgr.info('Querying info for subject %s', sub)
    for fr in query_files(platform, project=xnat_project, subject=sub):
        # communicate the query (makes outside error control possible)
        yield fr
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
