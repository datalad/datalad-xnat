# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test xnat-update

"""

from datalad.api import (
    Dataset,
    xnat_update,
)

from datalad.tests.utils_pytest import (
    assert_in_results,
    with_tempfile,
)

from datalad_xnat.init import _cfg_dataset


def fake_init(path=None):
    """Do whatever is needed to xnat-init() a fresh dataset without talking
    to a real XNAT instance
    """
    ds = Dataset(path).create()
    _cfg_dataset(
        ds,
        'https://example.com',
        'dummy_project',
        'dummy_subject',
        'dummy_experiment',
        'dummy_collection',
        '{subject}/{session}/{scan}/',
        'nocredential',
    )
    ds.run_procedure(spec='cfg_xnat_dataset')
    return ds


@with_tempfile
def test_invalid(path=None):
    ds = fake_init(path)
    (ds.pathobj / 'dirty').write_text('dirt')
    # refuses to work on dirty datasets
    assert_in_results(
        ds.xnat_update(on_failure='ignore'),
        status='impossible',
        action='update')
