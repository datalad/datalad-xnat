.. _python:

Python API
==========

``datalad-xnat`` has three main commands that are exposed as functions via ``datalad.api`` and as methods of the ``Dataset`` class: ``xnat_init`` for configuring a dataset to track XNAT projects, ``xnat_update`` for updating and retrieving files from tracked XNAT projects, and ``xnat_query-files`` for querying available files on an XNAT server.
Find out more about each command below.

.. currentmodule:: datalad.api
.. autosummary::
   :toctree: generated

   xnat_init
   xnat_query_files
   xnat_update
