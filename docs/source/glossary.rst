..  _glossary:

Glossary
========

.. glossary::

   credentials
       Something used to authenticate to a server, typically a username and a password. Datalad-xnat may prompt you for your credentials or use ones which have been previously saved (in datalad configuration or system keyring, see `datalad docs on credential management <https://docs.datalad.org/en/stable/design/credentials.html>`_). Some XNAT servers allow anonymous access (without checking credentials).

   experiment
       In XNAT terms, an experiment is an event by which data is acquired. This data can be imaging data, or non-imaging data. It exists within the context of a :term:`project`, but can be registered into multiple :term:`project`\s. Most experiments will be imaging :term:`session`\s.

   project
       A project is used to define a collection of data stored in XNAT. These often correlate directly to an IRB approved study, or a multi-site data acquisition program. Within XNAT, the project is used to define a security structure for data. Users are given certain permissions for data within certain projects -- thus, as a user you may not have permissions for all projects on a given XNAT instance.

   session
       In XNAT, an image session is a specific kind of an :term:`experiment` which contains image data. A session groups together multiple scans, where a scan corresponds to a DICOM series or BIDS data acquisition / run.

   subdataset
      A DataLad dataset contained within a different DataLad dataset (the parent or DataLad :term:`superdataset`).

   subject
       A subject is anyone who participates in a study, and exist within the context of a :term:`project`. Subjects can be registered in multiple :term:`project`\s (e.g., to capture longitudinal data from various studies).

   superdataset
       A DataLad dataset that contains one or more levels of other DataLad datasets (DataLad :term:`subdataset`\s).

   XNAT
      XNAT is an open source imaging informatics platform developed by the Neuroinformatics Research Group at Washington University. It facilitates common management, productivity, and quality assurance tasks for imaging and associated data. Imaging centers can operate an XNAT instance to manage their imaging acquisitions. Typically, they require a user name and password to gain access.
