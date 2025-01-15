Testing your calculator app
===========================

.. test:case:: Summarize and Clear values in calculator

    .. test:action:: Open :test:file:`signal.wav` in filein and press <Start>

        .. test:reaction:: The file is loaded and played. Ensure speakers active

    .. test:action:: Open :test:file:`signals/test1.wav` in the app

        .. test:reaction:: The file is loaded and shown in the edit tab.

        
    .. test:action:: Open :test:file:`/a/b/c/filein/test2.snd` in the app with url

        .. test:reaction:: The file is loaded and shown in the edit tab.


Appendix
--------

.. test:filelist::

