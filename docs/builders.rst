.. _builders:

Builders
========

.. _testspec_builder:

testspec
--------

The **testspec** builder exports all referenced files (see :rst:role:`file`) in the testspecification to a single json file

The build creates a folder called **testspec** and a file called **testspec.json** inside the given build-folder.


Usage
+++++

.. code-block:: bash

    sphinx-build -b testspec source_dir build_dir


.. hint::

   As an alternative the file is also created as ``testspec.json`` directly during the build of another output format like ``html``.
   The builder itself will be less more time consuming, but would give the same results.
   
