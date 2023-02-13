Testing your calculator app
===========================

.. test:case:: Summarize and Clear values in calculator

    .. test:action:: Type '2+2' into your systems calculator app and press '<enter>'.
        :id: ID_TEST_001

        .. test:reaction:: The calculator sums and shows you '4' as result.

    .. test:action:: Clear the results, e.g. by typing '<C>' or another button for clearing the results in your app
        :id: ID_TEST_002

        .. test:reaction:: The calculator does show '0' or shows nothing

    .. test:action::

        Repeat tests from :test:action:`ID_TEST_001` to :test:action:`ID_TEST_002` for the values of

        .. list-table::

        * - 3+3
          - 6
        * - 2+3
          - 5
        * - 1+3
          - 4
        * - 3+2
          - 5
        * - 3+4
          - 7
        * - 3+9
          - 12

        .. test:reaction:: The calculator does sum the values in the table correctly and the clear also works

