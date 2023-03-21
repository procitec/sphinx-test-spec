Testing your calculator app
===========================

.. test:case:: Summarize and Clear values in calculator

    .. test:action:: Open :test:file:`example.wav` in filein and press <Start>

        .. test:reaction:: The file is loaded and played. Ensure speakers active

    .. test:action:: Open :test:file:`example.zvd` in the app

        .. test:reaction:: The file is loaded and shown in the edit tab.


Appendix
--------

.. test:filelist::
    :filter: '.zvd' in suffix
