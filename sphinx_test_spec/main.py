import os
import posixpath
from html import escape
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version

from sphinx.errors import ConfigError, ExtensionError
from sphinx.util import logging

from sphinx_test_spec.artifacts import TESTSPEC_MANIFEST_FILENAME, write_testspec_manifest
from sphinx_test_spec.builder import TestSpecBuilder, build_testspec_artifacts
from sphinx_test_spec.domain import MESSAGE_CATALOG_NAME, TestSpecDomain
from sphinx_test_spec.forms import RESULT_VALUES
from sphinx_test_spec.pdf_forms import PdfFormProcessingError, normalize_weasyprint_form_pdf

LOG = logging.getLogger(__name__)
PACKAGE_NAME = "sphinx-test-spec"


def get_extension_version() -> str:
    """Return the installed package version from package metadata."""
    try:
        return package_version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0+unknown"


def rst_testspec_jinja(app, docname, source):
    """Render source files as Jinja templates when the builder supports templates."""
    if not hasattr(app.builder, "templates"):
        return

    src = source[0]
    rendered = app.builder.templates.render_string(src, app.config.testspec_context)
    source[0] = rendered


def validate_testspec_config(app) -> None:
    if app.config.testspec_result_mode not in {"symbol", "form"}:
        raise ConfigError("testspec_result_mode must be either 'symbol' or 'form'")

    unknown_labels = set(app.config.testspec_result_labels) - set(RESULT_VALUES)
    if unknown_labels:
        names = ", ".join(sorted(unknown_labels))
        raise ConfigError(f"testspec_result_labels contains unknown result keys: {names}")


def add_manifest_attachment_link(app, pagename, templatename, context, doctree) -> None:
    del templatename, doctree

    if not app.config.testspec_attach_manifest:
        return
    if pagename != app.config.master_doc:
        return

    # SimplePDF converts the generated HTML before Sphinx emits
    # build-finished. The attachment target therefore has to exist already.
    write_testspec_manifest(app, app.outdir)

    target_uri = app.builder.get_target_uri(pagename)
    target_dir = posixpath.dirname(target_uri)
    relative_manifest = posixpath.relpath(TESTSPEC_MANIFEST_FILENAME, start=target_dir or ".")
    attachment = (
        f'<link rel="attachment" href="{escape(relative_manifest, quote=True)}" title="Test specification manifest">'
    )
    context["metatags"] = f"{context.get('metatags', '')}\n{attachment}"


def finalize_testspec_build(app, exception) -> None:
    build_testspec_artifacts(app, exception)
    if exception is not None:
        return
    if getattr(app.builder, "name", "") != "simplepdf":
        return

    file_name = getattr(app.config, "simplepdf_file_name", None) or f"{app.config.project}.pdf"
    pdf_path = os.path.join(app.outdir, file_name)
    if not os.path.isfile(pdf_path):
        LOG.warning("could not normalize test-spec PDF forms because %s does not exist", pdf_path)
        return

    try:
        groups = normalize_weasyprint_form_pdf(pdf_path)
    except PdfFormProcessingError as exc:
        raise ExtensionError(f"failed to normalize generated test-spec PDF forms: {exc}") from exc
    LOG.info("normalized %d test-spec radio group(s) in %s", groups, pdf_path)


def setup(app):
    app.add_config_value("testspec_state_symbol", "", "html", [str])
    app.add_config_value("testspec_header", [], "html", [list])
    app.add_config_value("testspec_header_widths", [], "html", [list])
    app.add_config_value("testspec_context", {}, "html", [dict])
    app.add_config_value("testspec_result_mode", "symbol", "html", [str])
    app.add_config_value(
        "testspec_result_labels",
        {"passed": "✓", "failed": "✗", "na": "–"},
        "html",
        [dict],
    )
    app.add_config_value("testspec_comment_label", "Comment", "html", [str])
    app.add_config_value("testspec_namespace", "", "env", [str])
    app.add_config_value("testspec_document_id", "", "env", [str])
    app.add_config_value("testspec_attach_manifest", True, "html", [bool])

    app.add_domain(TestSpecDomain)
    app.add_builder(TestSpecBuilder)

    app.connect("builder-inited", validate_testspec_config)
    app.connect("source-read", rst_testspec_jinja)
    app.connect("html-page-context", add_manifest_attachment_link)
    app.connect("build-finished", finalize_testspec_build)

    package_dir = os.path.abspath(os.path.dirname(__file__))
    locale_dir = os.path.join(package_dir, "locales")
    LOG.debug(f"using locale dir {locale_dir}")
    app.add_message_catalog(MESSAGE_CATALOG_NAME, locale_dir)

    return {
        "version": get_extension_version(),
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
