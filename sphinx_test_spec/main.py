import os
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version

from sphinx.util import logging

from sphinx_test_spec.builder import TestSpecBuilder, build_testspec_json
from sphinx_test_spec.domain import MESSAGE_CATALOG_NAME, TestSpecDomain

LOG = logging.getLogger(__name__)
PACKAGE_NAME = "sphinx-test-spec"  # bzw. "sphinx-rst-table"


def get_extension_version() -> str:
    """Return the installed package version from package metadata.

    The version is maintained in ``pyproject.toml`` only. When the package is
    installed, that value is exposed through Python package metadata and used
    by Sphinx in ``setup()``. The fallback is only for direct source-tree usage
    without an installed distribution.
    """
    try:
        return package_version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0+unknown"


def rst_testspec_jinja(app, docname, source):
    """
    Render our pages as a jinja template for fancy templating goodness.
    """
    # Make sure we're outputting HTML
    if not hasattr(app.builder, "templates"):
        return

    src = source[0]
    rendered = app.builder.templates.render_string(src, app.config.testspec_context)
    source[0] = rendered


def setup(app):
    app.add_config_value("testspec_state_symbol", "", "html", [str])
    app.add_config_value("testspec_header", [], "html", [list])
    app.add_config_value("testspec_header_widths", [], "html", [list])
    app.add_config_value("testspec_context", {}, "html", [dict])

    app.add_domain(TestSpecDomain)

    app.add_builder(TestSpecBuilder)

    app.connect("source-read", rst_testspec_jinja)
    app.connect("build-finished", build_testspec_json)

    package_dir = os.path.abspath(os.path.dirname(__file__))
    locale_dir = os.path.join(package_dir, "locales")
    LOG.debug(f"using locale dir {locale_dir}")
    app.add_message_catalog(MESSAGE_CATALOG_NAME, locale_dir)

    return {
        "version": get_extension_version(),
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
