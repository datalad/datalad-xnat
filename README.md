# DataLad extension tracking data in an XNAT server
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-10-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![GitHub release](https://img.shields.io/github/release/datalad/datalad-xnat.svg)](https://GitHub.com/datalad/datalad-xnat/releases/) [![PyPI version fury.io](https://badge.fury.io/py/datalad-xnat.svg)](https://pypi.python.org/pypi/datalad-xnat/) [![Build status](https://ci.appveyor.com/api/projects/status/7pug8bjjgdcvsfn7/branch/master?svg=true)](https://ci.appveyor.com/project/mih/datalad-xnat/branch/master) [![codecov.io](https://codecov.io/github/datalad/datalad-xnat/coverage.svg?branch=master)](https://codecov.io/github/datalad/datalad-xnat?branch=master) [![crippled-filesystems](https://github.com/datalad/datalad-xnat/workflows/crippled-filesystems/badge.svg)](https://github.com/datalad/datalad-xnat/actions?query=workflow%3Acrippled-filesystems)
[![Documentation Status](https://readthedocs.org/projects/datalad-xnat/badge/?version=latest)](http://docs.datalad.org/projects/datalad-xnat/en/latest/?badge=latest)


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

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://psychoinformatics.de"><img src="https://avatars.githubusercontent.com/u/136479?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Michael Hanke</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=mih" title="Code">💻</a> <a href="https://github.com/datalad/datalad-xnat/issues?q=author%3Amih" title="Bug reports">🐛</a> <a href="https://github.com/datalad/datalad-xnat/commits?author=mih" title="Documentation">📖</a> <a href="#ideas-mih" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-mih" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/loj"><img src="https://avatars.githubusercontent.com/u/15157717?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Laura Waite</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=loj" title="Code">💻</a> <a href="https://github.com/datalad/datalad-xnat/issues?q=author%3Aloj" title="Bug reports">🐛</a> <a href="#ideas-loj" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-loj" title="Maintenance">🚧</a></td>
    <td align="center"><a href="http://www.adina-wagner.com"><img src="https://avatars.githubusercontent.com/u/29738718?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Adina Wagner</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=adswa" title="Code">💻</a> <a href="https://github.com/datalad/datalad-xnat/issues?q=author%3Aadswa" title="Bug reports">🐛</a> <a href="https://github.com/datalad/datalad-xnat/commits?author=adswa" title="Documentation">📖</a> <a href="#ideas-adswa" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-adswa" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/jwodder"><img src="https://avatars.githubusercontent.com/u/98207?v=4?s=100" width="100px;" alt=""/><br /><sub><b>John T. Wodder II</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=jwodder" title="Code">💻</a> <a href="#ideas-jwodder" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="http://www.onerussian.com"><img src="https://avatars.githubusercontent.com/u/39889?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Yaroslav Halchenko</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=yarikoptic" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/JanviRaina"><img src="https://avatars.githubusercontent.com/u/50794649?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Janvi Raina</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=JanviRaina" title="Documentation">📖</a></td>
    <td align="center"><a href="https://jsheunis.github.io/"><img src="https://avatars.githubusercontent.com/u/10141237?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Stephan Heunis</b></sub></a><br /><a href="#infra-jsheunis" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#design-jsheunis" title="Design">🎨</a> <a href="#mentoring-jsheunis" title="Mentoring">🧑‍🏫</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/tsankeuodelfa"><img src="https://avatars.githubusercontent.com/u/83062549?v=4?s=100" width="100px;" alt=""/><br /><sub><b>tsankeuodelfa</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=tsankeuodelfa" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/mslw"><img src="https://avatars.githubusercontent.com/u/11985212?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Michał Szczepanik</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=mslw" title="Documentation">📖</a> <a href="https://github.com/datalad/datalad-xnat/commits?author=mslw" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/bpoldrack"><img src="https://avatars.githubusercontent.com/u/10498301?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Benjamin Poldrack</b></sub></a><br /><a href="https://github.com/datalad/datalad-xnat/commits?author=bpoldrack" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!