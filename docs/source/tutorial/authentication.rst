.. _authentication:

Authentication
==============

"Oh no, I accidentally mistyped my password!"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you supplied wrong credentials, or previously working credentials expired and
stopped working, you can re-enter new credentials with the configuration
``datalad.credentials.force-ask=1``:

.. code-block:: bash

   $ datalad -c datalad.credentials.force-ask=1 xnat-init <url>
   You need to authenticate with [...]
   user: <user>
   password: <password>

Alternatively, find your system's secure Keyring (your systems credential store) and remove or replace your password in there.