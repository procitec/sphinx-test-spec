Manual result workflow
======================

``sphinx-test-spec`` can generate a form-oriented HTML document that WeasyPrint turns into an AcroForm PDF.
The filled PDF can then be converted directly into JUnit with the installed ``testspec-result`` command.

Identity model
--------------

A test id consists of three independent parts::

    <execution-prefix>.<testspec-namespace>.<test-case-id>

For example::

    linux.category.appname.startup
    windows.category.appname.startup

``testspec_namespace`` and the test case ``:id:`` are fixed when the specification is built. The execution prefix
is deliberately added later so that the same PDF can be executed on multiple target platforms.

PDF form layout
---------------

Each action/reaction pair remains one compact table row. In form mode the last column contains one three-way
radio-button group. The configured labels are shown once in the table header and the rows themselves contain only
the three radio buttons. This keeps the result column narrow while retaining the stable form values ``passed``,
``failed`` and ``na``.

A compact configuration is for example::

    testspec_result_mode = "form"
    testspec_header = ["Nr.", "Aktion", "Reaktion", ""]
    testspec_header_widths = [6, 45, 42, 7]
    testspec_result_labels = {
        "passed": "✓",
        "failed": "✗",
        "na": "–",
    }
    testspec_comment_label = "Anmerkung"

With the configuration above the fourth header is rendered as ``✓  ✗  –`` and every result row as three aligned
radio buttons. Header and row use the same non-wrapping three-part flex layout so Sphinx theme CSS cannot move the
buttons below each other.

The generated HTML uses CSS classes ``testspec-result-passed``, ``testspec-result-failed`` and
``testspec-result-na``. Projects can therefore add their own colours or other styling without changing the
result-processing semantics.

The form controls use ``appearance: auto``. This means that WeasyPrint creates AcroForm fields without requiring
the global ``--pdf-forms`` option. If ``sphinx-simplepdf`` uses WeasyPrint's API instead of the command-line
interface, the same mechanism still works.

For ``simplepdf`` form builds, ``sphinx-test-spec`` performs a small post-processing step on the generated PDF.
WeasyPrint's radio widgets are converted into one conventional AcroForm radio group per action/reaction row. Each
widget gets a complete vector appearance for both states: an empty circle for ``Off`` and a circle with an inner dot
for the selected state. This avoids viewer-dependent live redraw behaviour and also gives printing a real appearance
stream for unselected and selected buttons. The semantic field values remain ``passed``, ``failed`` and ``na``.

Manifest
--------

``testspec-manifest.json`` contains the document identity, specification hash, build-time namespace, stable case
ids, the ordered action/reaction pairs and their technical PDF form-field names. If ``testspec_attach_manifest``
is enabled (default), the HTML master page references this file as an attachment so WeasyPrint embeds it in the
PDF.

The specification hash covers the semantic test specification, but not execution-specific data, comments or
form-field names. The same PDF can therefore be executed for Linux and Windows while retaining the same
specification identity.

Result extraction
-----------------

After filling the PDF, create JUnit with::

    testspec-result executed.pdf \
        --execution-prefix linux \
        --junit result.xml

The normalized intermediate result can additionally be written as JSON::

    testspec-result executed.pdf \
        --execution-prefix linux \
        --junit result.xml \
        --result-json result.json

Normally the embedded ``testspec-manifest.json`` is used. An external manifest can be supplied as a fallback or
for additional verification::

    testspec-result executed.pdf \
        --manifest testspec-manifest.json \
        --execution-prefix linux \
        --junit result.xml

If both an embedded and an external manifest exist, their specification hashes must match.

Aggregation
-----------

Each action/reaction row has one result field with ``passed``, ``failed`` or ``na``. The complete test case is
aggregated as follows:

* all result fields empty -> JUnit ``skipped`` (not executed)
* any ``failed`` -> JUnit ``failure``
* some fields filled and some empty -> JUnit ``error`` (incomplete execution)
* all fields filled and all ``na`` -> JUnit ``skipped`` (not applicable)
* otherwise, all fields ``passed`` or ``na`` with at least one ``passed`` -> passed

There is one comment field per ``test:case``. A stable ``:id:`` is mandatory for JUnit export, because the final
qualified id is used for the existing ``:acc:`` mapping.

The conversion itself returns successfully even if test cases are failed, skipped or incomplete. Those states are
encoded in JUnit. The command returns an error only if the PDF/manifest cannot be processed safely.
