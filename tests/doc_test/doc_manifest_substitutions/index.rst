Manifest substitution and ID test
=================================

.. test:case:: Verify |branding_camel_name|
   :id: CASE_100

   .. test:action::
      :id: ACTION_START

      Start |branding_camel_name|.

      .. test:reaction::
         :id: REACTION_STARTED

         |branding_camel_name| shows the ``Ready`` state.

   .. test:action::

      Stop |branding_camel_name|.

      .. test:reaction::

         |branding_camel_name| is stopped.

.. test:case:: Verify repeated steps
   :id: CASE_200

   .. test:action::
      :id: ACTION_START

      Start |branding_camel_name| again.

      .. test:reaction::
         :id: REACTION_STARTED

         |branding_camel_name| is available again.

   .. test:action::
      :id: ACTION_ONLY

      Check |branding_camel_name| status.

      .. test:reaction::

         The status is displayed.

   .. test:action::

      Read the displayed status.

      .. test:reaction::
         :id: REACTION_ONLY

         |branding_camel_name| is ready.
