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
    xnat_init,
)
from datalad.tests.utils_pytest import (
    assert_result_count,
    with_tempfile,
)
from datalad.utils import Path


@with_tempfile
def test_invalid_url(dspath=None):

    dspath = Path(dspath)

    ds = Dataset(dspath).create()

    # URL not found:
    res = ds.xnat_init('https://example.com',
                       project='no_such_DICOM',
                       credential='anonymous',
                       on_failure='ignore')
    assert_result_count(res, 1, status='error',
                        message='Request to XNAT server failed: Not Found')

# TODO:

# - test no project given (ATM: No result dict, no exception)

# - authenticated access w/ and w/o valid credentials
# - authenticated access w/ inaccessible credentials
#   ("non-interactive reference to non-existent credentials yields Authorization
#   required for https://example.com, cannot find token for a credential
#   non-existent.")
# - authenticated re-execution of init should error-out w/o force

