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
from datalad.tests.utils import (
    assert_result_count,
    with_tempfile,
)
from datalad.utils import Path


@with_tempfile
def test_invalid_url(dspath):

    dspath = Path(dspath)

    ds = Dataset(dspath).create()

    # URL not found:
    res = ds.xnat_init('https://example.com',
                       project='no_such_DICOM',
                       credential='anonymous',
                       on_failure='ignore')
    assert_result_count(res, 1, status='error',
                        message='Request to XNAT server failed: Not Found')


