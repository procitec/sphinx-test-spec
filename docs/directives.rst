.. _directives:

Directives
==========

.. rst:directive:: :test:case

    A test scenario or test case is added with this directive

    .. code-block:: rst

        .. :test:case: Title for the Test Case

    The title is required (e.g. for references).
    A section is added with this title. The sections could be numbered with the ``.. toctree`` ``:numbered:`` option.

    .. rubric:: Options

    .. rst:directive:option:: class
    :type: str

    The class name for html output to use in css files. This will be appended to the directive classes.


.. rst:directive:: :test:action

    A test step is added with `test:action`.
    This descripes the action the tester has to perform.

    In the output this directive creates a new row in the test actions table.

    .. rubric:: Options

    .. rst:directive:option:: class
        :type: str

        The class name for html output to use in css files. This will be appended to the directive classes.


.. rst:directive:: :test:reaction

    A test reaction description is added to the output.

    This directive has to occur as part of the content of a `test:action` directive.
    This content will be added to the current `test:action` on the same row.

    If the `test:action` has no reaction that should be mentioned, just ommit this directive.
    An empty cell will be added in this case.

    .. code-block:: rst

        .. test:action:: Enter your valid password in the password field and press <enter>

            .. test:reaction:: The login form dissapears and the content is shown

    .. rubric:: Options

    .. rst:directive:option:: class
        :type: str
        
        The class name for html output to use in css files. This will be appended to the directive classes.
