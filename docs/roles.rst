.. _roles:

Roles
=====

The `Test` Domain supports following rules for crossreferencing:

.. rst:role:: test:case

    To add a reference to a test case, add :code:`:test:case:`title``

.. rst:role:: test:file

    To add a reference to a test file, add :code:`:test:file:`filename``.
    The filename is not checked for existence, just added to be referenced by the :code:`:test:filelist:` directive.
    The filename is shown as `EmphasizedLiteral` in the text.
