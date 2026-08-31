.. _builders:

Builders
========

.. _testspec_builder:

testspec
--------

The **testspec** builder exports the machine-readable artifacts collected from the test specification.

The build creates a folder called **testspec** with these files inside the given build folder:

``testspec-resources.json``
    Referenced files (see :rst:role:`file`) required to execute the tests. This is the renamed form of the
    former ``testspec.json`` artifact; its JSON content is unchanged. A stale legacy ``testspec.json`` in the
    output directory is removed when the new resource artifact is written.

``testspec-manifest.json``
    Test document identity, build-time namespace, test case ids, linear action/reaction steps, PDF form field
    names and a SHA-256 specification hash.

Usage
+++++

.. code-block:: bash

    sphinx-build -b testspec source_dir build_dir

.. hint::

   Both files are also created directly during other builds such as ``html``. The dedicated builder skips the
   normal write phase and is therefore useful when only the machine-readable artifacts are required.

PDF forms and manifest attachment
+++++++++++++++++++++++++++++++++

With ``testspec_result_mode = "form"`` the HTML output keeps the existing one-row-per-action layout and replaces
only the last column with the compact configured result radio buttons. One comment field is added per test case.

If ``testspec_attach_manifest`` is enabled, the HTML master document references ``testspec-manifest.json`` with
``rel="attachment"``. WeasyPrint embeds this file into the PDF when it renders the HTML.

Result conversion
-----------------

The installed ``testspec-result`` command reads a filled PDF, validates/extracts the embedded manifest and writes
JUnit XML. The execution-specific namespace prefix is supplied during conversion, for example::

    testspec-result executed.pdf --execution-prefix linux --junit result.xml

The same PDF can therefore be executed for multiple target platforms without rebuilding the specification.
