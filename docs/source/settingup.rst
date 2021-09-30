.. include:: ./links.inc

.. _install:

Quickstart
==========

Requirements
^^^^^^^^^^^^

DataLad and ``datalad-xnat`` are available for all major operating systems (Linux, MacOS, Windows 10 [#f1]_).
The relevant requirements are listed below.

   An XNAT_ account with appropriate permissions
       You need access to an XNAT_ server to able to interact with it, and appropriate permissions to access the projects you are interested in.
       Keep your XNAT_ instance's URL and your user name and password to your account close by.

   DataLad
       If you don't have DataLad_ and its underlying tools (`git`_, `git-annex`_) installed yet, please follow the instructions from `the datalad handbook <http://handbook.datalad.org/en/latest/intro/installation.html>`_.


Installation
^^^^^^^^^^^^

``datalad-xnat`` is a Python package available on `pypi <https://pypi.org/project/datalad-xnat/>`_ and installable via pip_.

.. code-block:: bash

   # create and enter a new virtual environment (optional)
   $ virtualenv --python=python3 ~/env/dl-xnat
   $ . ~/env/dl-xnat/bin/activate
   # install from PyPi
   $ pip install datalad-xnat

Getting started
^^^^^^^^^^^^^^^

Here's the gist of some of this extension's functionality.
Checkout the :ref:`Tutorial` for more detailed demonstrations.

Start by creating and initializing a new DataLad dataset to track a specific
XNAT project. This example uses the `XNAT central <https://central.xnat.org/>`_
instance with anonymous credentials for the project `DCMPHANTOM <https://central.xnat.org/app/action/DisplayItemAction/search_element/xnat%3AprojectData/search_field/xnat%3AprojectData.ID/search_value/DCMPHANTOM>`_.

.. code-block::

   $ datalad create dcm_phantom
   $ cd dcm_phantom
   $ datalad xnat-init https://central.xnat.org --credential anonymous --project DCMPHANTOM

After initialization, run ``xnat-update`` to download all files for the project.

.. code-block::

   $ datalad xnat-update --credential anonymous --subject CENTRAL_S01742


.. admonition:: HELP! I'm new to this!

   If you are confused about the words DataLad dataset,  please head over to the `DataLad Handbook`_ for an introduction to DataLad.

   If you are confused about the words project, experiment, or session in the context of XNAT, take a look at the :ref:`glossary` or in the `XNAT documentation <https://wiki.xnat.org/docs>`_.

.. rubric:: Footnotes

.. [#f1] While installable for Windows 10, the extension may not be able to perform all functionality documented here. Please get in touch if you are familiar with Windows `to help us fix bugs <https://github.com/datalad/datalad-xnat>`_.
