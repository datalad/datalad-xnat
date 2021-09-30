# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Integration tests for XNAT central

"""

from datalad.api import (
    Dataset,
)

from datalad.tests.utils import (
    assert_in_results,
    with_tempfile,
)


@with_tempfile
def test_anonymous_access(path):
    ds = Dataset(path).create()
    assert_in_results(
        ds.xnat_init(
            'https://central.xnat.org',
            project='IDONOTEXIST_used_in_datalad-xnat_CI',
            credential='anonymous',
            on_failure='ignore'),
        status='error',
        action='xnat_init')
    # minimal demo dataset (pulls .5MB from xnat central)
    ds.xnat_init(
        'https://central.xnat.org',
        project='Sample_DICOM',
        credential='anonymous')
    ds.xnat_update(
        # must be a subject's accession ID
        subjects='CENTRAL_S01894',
    )
    # we get the project's payload DICOM in the expected location
    assert_in_results(
        ds.status(annex='availability'),
        key='MD5E-s533936--b402d6341f5894c63c991c6361ad14ff.dcm',
        has_content=True,
        path=str(ds.pathobj / 'CENTRAL_S01894' / 'CENTRAL_E03907' / '2' /
                 'dcmtest1.MR.Sample_DICOM.2.1.20010108.120022.1azj8tu.dcm'),
        state='clean',
        type='file',
    )
