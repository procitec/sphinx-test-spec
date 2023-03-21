import os

import sphinx
from pkg_resources import parse_version
from sphinx.util import logging

from sphinx_test_spec.domain import MESSAGE_CATALOG_NAME, TestSpecDomain

LOG = logging.getLogger(__name__)
VERSION = 0.1


def rst_testspec_jinja(app, docname, source):
    """
    Render our pages as a jinja template for fancy templating goodness.
    """
    ## Make sure we're outputting HTML
    # if app.builder.format != 'html':
    #    return
    src = source[0]
    rendered = app.builder.templates.render_string(src, app.config.testspec_context)
    source[0] = rendered
    # print(f"rendered = {rendered}")


def setup(app):
    app.add_config_value("testspec_state_symbol", "", "html", [str])
    app.add_config_value("testspec_header", [], "html", [list])
    app.add_config_value("testspec_header_widths", [], "html", [list])
    app.add_config_value("testspec_context", {}, "html", [dict])

    app.add_domain(TestSpecDomain)

    app.connect("source-read", rst_testspec_jinja)

    package_dir = os.path.abspath(os.path.dirname(__file__))
    locale_dir = os.path.join(package_dir, "locales")
    LOG.debug((f"using locale dir {locale_dir}"))
    app.add_message_catalog(MESSAGE_CATALOG_NAME, locale_dir)

    return {"version": VERSION, "parallel_read_safe": True, "parallel_write_safe": True}
