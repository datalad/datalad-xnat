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

from datalad.tests.utils_pytest import (
    assert_equal,
    assert_in,
    assert_in_results,
    assert_raises,
    with_tempfile,
)

from ..platform import (
    _XNAT,
    XNATRequestError,
)


# The following constants define what to test w/ or against wrt to xnatcentral
# Idea: 1. Changes would be easy to apply to all tests
#       2. May turn into more generic tests that can be used with different
#          targets
XNAT_URL = "https://central.xnat.org"
XNAT_CREDENTIAL = "anonymous"
NON_EXISTENT_PROJECT = NON_EXISTENT_SUBJECT = NON_EXISTENT_EXPERIMENT = \
    "IDONOTEXIST_used_in_datalad-xnat_CI"
PROJECT = "Sample_DICOM"
SUBJECT = "CENTRAL_S01894"
N_SUBJECTS = 2
EXPERIMENT = "CENTRAL_E03907"
SCAN = "2"
FILE = "dcmtest1.MR.Sample_DICOM.2.1.20010108.120022.1azj8tu.dcm"
FILE_KEY = "MD5E-s533936--b402d6341f5894c63c991c6361ad14ff.dcm"


def test_anonymous_access_platform():
    # test platform object w/ anonymous access to xnatcentral

    platform = _XNAT(XNAT_URL, credential=XNAT_CREDENTIAL)

    # test project info functions
    project_ids = platform.get_project_ids()
    assert_in(PROJECT, project_ids)
    assert_equal(set(project_ids),
                 set([p['ID'] for p in platform.get_projects()]))

    # test subject info functions
    assert_raises(XNATRequestError, platform.get_nsubjs,
                  NON_EXISTENT_PROJECT)
    assert_raises(XNATRequestError, platform.get_subject_ids,
                  NON_EXISTENT_PROJECT)

    assert_equal(N_SUBJECTS, platform.get_nsubjs(PROJECT))
    subjects = platform.get_subject_ids(PROJECT)
    assert_equal(N_SUBJECTS, len(subjects))
    assert_in(SUBJECT, subjects)

    # test experiment info functions
    assert_equal([],
                 platform.get_experiment_ids(project=NON_EXISTENT_PROJECT,
                                             subject=NON_EXISTENT_SUBJECT))

    experiments = platform.get_experiment_ids(project=PROJECT, subject=SUBJECT)
    assert_equal([EXPERIMENT], experiments)
    assert_equal([EXPERIMENT],
                 [e['ID'] for e in platform.get_experiments(project=PROJECT,
                                                            subject=SUBJECT)]
                 )

    # test scan info functions
    assert_in(SCAN, platform.get_scan_ids(EXPERIMENT))
    assert_raises(XNATRequestError,
                  platform.get_scan_ids, NON_EXISTENT_EXPERIMENT)


@with_tempfile
def test_anonymous_access_api(path=None):
    # test command usage w/ anonymous access to xnatcentral

    ds = Dataset(path).create()
    # minimal demo dataset (pulls .5MB from xnat central)
    ds.xnat_init(
        XNAT_URL,
        project=PROJECT,
        subject=SUBJECT,
        pathfmt='{subject}//{session}/{scan}/',
        credential=XNAT_CREDENTIAL)
    ds.xnat_update(
        # must be a subject's accession ID
        jobs=2,
    )
    # we get the project's payload DICOM in the expected location
    assert_in_results(
        ds.status(annex='availability', recursive=True),
        key=FILE_KEY,
        has_content=True,
        path=str(ds.pathobj / SUBJECT / EXPERIMENT / SCAN / FILE),
        state='clean',
        # this seems like a bug, in subdatasets type='symlink'...
        # type='file',
    )
