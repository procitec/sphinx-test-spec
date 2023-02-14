sphinx-test-spec
================

Sphinx extension to support definition of manual tests cases.

The extension adds a Domain `test` to Sphinx to define Test Cases with Actions and possible Reactions as tables.

While this could also be achieved using normal Sphinx or RestructuredText tables the extension helps with:

* Adding an autonumbered **id** column to the test procedure tables for unique test enumeration and autoupdated
  crossreferences

* Adding each test case as section in the output with autolevel determination by the outer section levels

* Adding a `ok` column with configuration option to add unique content to show (e.g. a unicode ballot box for  checkboxes).

* Textual representation of the test-actions / reactions pairs due to nested directive declartion

* Full content parsing of the content in the directives for ease of using custom content like

    - images
    - nested lists or tables
    - and further sphinx features

While there are several frameworks available to describe tests in a better way (see Behaviour Driven Development), this extension tries to help in writing manual test specifiations in a tabular way.


.. code:: rst

    Testing your calculator app
    ===========================

    .. test:case:: Summarize and Clear values in calculator

        .. test:action:: Type '2+2' into your systems calculator app and press '<enter>'.

            .. test:reaction:: The calculator sums and shows you '4' as result.

        .. test:action:: Clear the results, e.g. by typing '<C>' or another button for clearing the results in your app

            .. test:reaction:: The calculator does show '0' or shows nothing


Documentation
-------------

See `doc/index.rst` for the documentation.

Examples/Tests
--------------

For examples look at the `test` directory in this repo. All automated tests could server as simple examples.

The tests could be run by running `nox` in the extension directory or by manually calling `make test`.

