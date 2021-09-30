.. include:: ./links.inc
.. _intro:

Introduction
============

XNAT
----

`XNAT`_ is an open source platform purpose-built for imaging data and
data associated with it. In addition to hosting and cataloging the data, XNAT
can assist with triggering quality assurance tasks and other workflows.

Goal of the extension
---------------------

[COMPLETE ME] What did we set out to do?

What can I use this extension for?
----------------------------------

[COMPLETE ME] Usecases for the extentions

What can I **not** use this extension for?
------------------------------------------

The list of valid use cases for this extension is much shorter than the list of
invalid use cases. You for example will not be able to open a bottle of your favourite
beverage with it (sorry).
But here is a list of invalid use cases that may be most relevant to know about:

- You can not use this extension as a *replacement* for an XNAT_ instance. It requires
  access to one, and tracks the data available on this instance.
- You *should* not use this extension to share data that you retrieved from an XNAT_ server
  publicly. While DataLad datasets are ideal for sharing large amounts of data publicly,
  the data from an XNAT_ server is usually not to be shared publicly - for example due to, but not limited to, privacy concerns. Please think twice before you attempt to do this.