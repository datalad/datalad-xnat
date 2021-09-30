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


def parse_xnat(outfile, platform, force=False,
               project=None, subject=None, experiment=None,
               collections=None):
    """Lookup specified subject for configured XNAT project and build csv table.

    Parameters
    ----------
    outfile: file-like
        Writable file descriptor.
    platform: str
        XNAT instance
    force: str
        Re-build csv table if it already exists.
    project: str
    subject: str
    experiment: str
    collections : list
        If given, a list of collection/resource labels to limit the results
        to.
    """
    # create csv table containing subject info & file urls
    table_header = ['subject', 'session', 'scan', 'filename', 'url']

    # write subject info to file
    fh = csv.writer(outfile, delimiter=',')
    fh.writerow(table_header)
    for fr in query_files(
            platform, project=project, subject=subject, experiment=experiment):
        if collections and fr.get('collection') not in collections:
            lgr.debug('File excluded by collection selection')
            continue
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
