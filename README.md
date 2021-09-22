# DataLad extension tracking data in an XNAT server

[![GitHub release](https://img.shields.io/github/release/datalad/datalad-xnat.svg)](https://GitHub.com/datalad/datalad-xnat/releases/) [![PyPI version fury.io](https://badge.fury.io/py/datalad-xnat.svg)](https://pypi.python.org/pypi/datalad-xnat/) [![Build status](https://ci.appveyor.com/api/projects/status/7pug8bjjgdcvsfn7/branch/master?svg=true)](https://ci.appveyor.com/project/mih/datalad-xnat/branch/master) [![codecov.io](https://codecov.io/github/datalad/datalad-xnat/coverage.svg?branch=master)](https://codecov.io/github/datalad/datalad-xnat?branch=master) [![crippled-filesystems](https://github.com/datalad/datalad-xnat/workflows/crippled-filesystems/badge.svg)](https://github.com/datalad/datalad-xnat/actions?query=workflow%3Acrippled-filesystems)

This software is a [DataLad](http://datalad.org) extension that equips DataLad
with a set of commands to track XNAT projects.

XNAT is an open source imaging informatics platform developed by the
Neuroinformatics Research Group at Washington University. It facilitates common
management, productivity, and quality assurance tasks for imaging and
associated data. XNAT can be used to support a wide range of neuro/medical
imaging-based projects.

Command(s) provided by this extension

- `xnat-init` -- Initialize an existing dataset to track an XNAT project
- `xnat-update` -- Update an existing dataset of an XNAT project


## Installation

Before you install this package, please make sure that you [install a recent
version of git-annex](https://git-annex.branchable.com/install).  Afterwards,
install the latest version of `datalad-xnat` from
[PyPi](https://pypi.org/project/datalad-xnat). It is recommended to use
a dedicated [virtualenv](https://virtualenv.pypa.io):

    # create and enter a new virtual environment (optional)
    virtualenv --system-site-packages --python=python3 ~/env/datalad
    . ~/env/datalad/bin/activate

    # install from PyPi
    pip install datalad_xnat


## Support

For general information on how to use or contribute to DataLad (and this
extension), please see the [DataLad website](http://datalad.org) or the
[main GitHub project page](http://datalad.org).

All bugs, concerns and enhancement requests for this software can be submitted here:
https://github.com/datalad/datalad-xnat/issues

If you have a problem or would like to ask a question about how to use DataLad,
please [submit a question to
NeuroStars.org](https://neurostars.org/tags/datalad) with a ``datalad`` tag.
NeuroStars.org is a platform similar to StackOverflow but dedicated to
neuroinformatics.

All previous DataLad questions are available here:
http://neurostars.org/tags/datalad/


## Acknowledgements

This development was supported by European Union’s Horizon 2020 research and
innovation programme under grant agreement [VirtualBrainCloud
(H2020-EU.3.1.5.3, grant no.
826421)](https://cordis.europa.eu/project/id/826421).
