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

    .. rst:directive:option:: id
        :type: str

        Stable identifier of the test case. It is used by ``testspec-manifest.json`` and can be
        combined with ``testspec_namespace`` and a later execution prefix to build the final test id.

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


.. rst:directive:: :test:filelist

    A list with all referenced files is added in place of the directive. The files are shown as list with path normalised to posix paths.

    .. rubric:: Options

    .. rst:directive:option:: filter
        :type: str

        Allows filtering of referenced files by one of ['name', 'suffix', 'parent'] according to `pathlib <https://docs.python.org/3/library/pathlib.html>`_.


    .. rst:directive:option:: class
        :type: str

        The class name for html output to use in css files. This will be appended to the directive classes.

.. rst:directive:: test:choice

    Adds a free single-choice group to the document. The group is independent of
    ``test:case`` results and is useful for execution metadata such as the target
    operating system, hardware variant, or test environment.

    The directive argument is used as the visible label. Each non-empty content
    line defines one choice. The choices are distributed evenly across one row.

    .. code-block:: rst

        .. test:choice:: Betriebssystem
           :id: operating-system

           Ubuntu
           RedHat
           Windows

    ``:id:`` is required and is used to create a stable PDF form field name.

    .. rubric:: Options

    .. rst:directive:option:: id
        :type: str

        Required stable identifier of the form field.

    .. rst:directive:option:: class
        :type: str

        Additional CSS class for the wrapper element.


.. rst:directive:: test:comment

    Adds a free multiline annotation field that is independent of a
    ``test:case``. The directive argument is used as the visible label.

    .. code-block:: rst

        .. test:comment:: Allgemeine Anmerkungen
           :id: general-notes
           :rows: 4

    .. rubric:: Options

    .. rst:directive:option:: id
        :type: str

        Required stable identifier of the form field.

    .. rst:directive:option:: rows
        :type: int
        :default: 4

        Number of visible text rows.

    .. rst:directive:option:: class
        :type: str

        Additional CSS class for the wrapper element.
