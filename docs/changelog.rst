Changelog
=========

26.3
----

- Preserve optional ``:id:`` values from ``test:action`` and ``test:reaction`` as
  ``action_id`` and ``reaction_id`` in the manifest, including in the specification hash.
- Resolve RST substitutions (including ``rst_prolog`` definitions) before storing
  case titles and action/reaction text in the JSON manifest.

26.2.8
------

- Add free ``test:choice`` and ``test:comment`` form directives for execution metadata and annotations.
- Normalize WeasyPrint radio groups after ``simplepdf`` generation and provide complete ``Off``/selected appearances with a visible outline. The original outline is masked so result and ``test:choice`` fields do not develop double circles.
- Add the standalone ``testspec-result`` PDF-to-JUnit/result-JSON converter.
- Add compact/configurable result labels and a configurable per-case comment label.
- Add ``pypdf`` as the runtime dependency for PDF result extraction.
- Rename the referenced-file artifact from ``testspec.json`` to ``testspec-resources.json``.
- Add stable ``:id:`` support for test cases and a ``testspec-manifest.json`` artifact.
- Add optional compact HTML/PDF result forms with PASS/FAIL/N/A per action and one comment per test case.
- Add build-time namespace and manifest attachment support for WeasyPrint based PDF workflows.

25.1
----

- Creation of ``testspec.json`` with information about referenced files in the document.
  The file is created during every build or with the specific **testspec** builder.
