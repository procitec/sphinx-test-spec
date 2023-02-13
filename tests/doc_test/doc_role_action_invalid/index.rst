Testing your calculator app
===========================

.. test:case:: Summarize and Clear values in calculator

    .. test:action:: Type '2+2' into your systems calculator app and press '<enter>'.
        :id: ID_TEST_001

        .. test:reaction:: The calculator sums and shows you '4' as result.

    .. test:action:: Clear the results, e.g. by typing '<C>' or another button for clearing the results in your app
        :id: ID_TEST_002

        .. test:reaction:: The calculator does show '0' or shows nothing



.. test:case:: Input in binary mode

    .. test:action:: Put your calculator app in input for binary values only

        .. test:reaction:: The calculator app does give visual feedback that binary mode input is enabled

    .. test:action:: Input the values '0110' in the app

        .. test:reaction:: The values are shown in the calculator app

    .. test:action::

        Try the steps from :test:action:`ID_TEST_001`


