Testing your calculator app
===========================

.. test:case:: Summarize and Clear values in calculator
    :class: custom-case

    This is free text before the table after the title

    .. test:action:: Type '2+2' into your systems calculator app and press '<enter>'.
        :class: custom-action

        .. test:reaction:: The calculator sums and shows you '4' as result.
            :class: custom-reaction

    .. test:action:: Clear the results, e.g. by typing '<C>' or another button for clearing the results in your app

        .. test:reaction:: The calculator does show '0' or shows nothing
