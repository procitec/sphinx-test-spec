import sphinx
from pkg_resources import parse_version
from sphinx.util import logging
import os

from sphinx_test_spec.domain import TestSpecDomain, MESSAGE_CATALOG_NAME

LOG = logging.getLogger(__name__)
VERSION = 0.1


def setup(app):
    app.add_config_value("testspec_state_symbol", '', "html", [str])
    app.add_config_value("testspec_header", [], "html", [list])
    app.add_config_value("testspec_header_widths", [], "html", [list])

    app.add_domain(TestSpecDomain)

    package_dir = os.path.abspath(os.path.dirname(__file__))
    locale_dir = os.path.join(package_dir, 'locales')
    LOG.debug((f"using locale dir {locale_dir}"))
    app.add_message_catalog(MESSAGE_CATALOG_NAME, locale_dir)

    return {"version": VERSION, "parallel_read_safe": True, "parallel_write_safe": True}
