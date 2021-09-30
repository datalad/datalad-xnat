.. include:: ../links.inc
.. _init:


Internals: Understanding xnat-init
==================================


Understanding the dataset configurations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One of the main functions of the ``datalad xnat-init`` command is to create a
dataset-internal configuration with information about the XNAT_ instance, the
directory structure for downloaded files, and the project to track.
This configuration is what determines the looks and feel of the final dataset,
in particular the presence and location of :term:`subdataset`\s, and the imaging
files you will be able to retrieve afterwards.

The individual components of these configurations are spread over two different
places in your dataset:

#. a DataLad configuration within ``.datalad/config``
#. a provider configuration within ``.datalad/providers/``

Both of these configurations are dataset-specific, i.e., configure only the
behavior of this particular dataset, not other datasets you may have on your
system.


The provider configuration
--------------------------

The first configuration created by ``datalad xnat-init`` is a so-called "provider configuration".
Provider configurations are small, plain text files that configure how a specific
service provider shall be accessed.
You can find general information on them in `the DataLad handbook <http://handbook.datalad.org/en/latest/beyond_basics/101-146-providers.html>`_.

The provider configuration created by ``datalad xnat-init`` lives in
``.datalad/providers/xnat-<name>.cfg``, where ``name`` is a placeholder for an
arbitrary identifier.
The default name is ``.datalad/providers/xnat-default.cfg``, but in case of datasets
that track projects from multiple different XNAT instances the identifier allows
to differentiate between them.

We can take a look into an exemplary configuration file:

.. code-block::

	[provider:xnat-default]
	url_re = https://xnat.kube.fz-juelich.de/.*
	credential = xnat.kube.fz-juelich.de
	authentication_type = http_basic_auth

	[credential:xnat.kube.fz-juelich.de]
	type = user_password

It specifies the URL to the XNAT instance supplied during ``datalad xnat-init``,
and determines the credential (such as authentication with a user name and a password)
and authentication (such `HTTP Basic Authentication <https://en.wikipedia.org/wiki/Basic_access_authentication>`_)
type.

The DataLad configuration
-------------------------

The second configuration created by ``datalad xnat-init`` is a DataLad
configuration that configures the dataset to use a given provider configuration.
It is included in the ``.datalad/config file`` and looks like this:

.. code-block:: bash

	[datalad "xnat.default"]
		url = https://xnat.kube.fz-juelich.de
		project = phantoms
		path = {subject}/{session}/{scan}/
		credential-name = xnat.kube.fz-juelich.de

Note how it identifies a provider configuration via its ``<name>``, and how it
includes the configuration about which XNAT project to track.

