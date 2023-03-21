from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys


@pytest.mark.parametrize(
    "test_app", [{"buildername": "html", "srcdir": "doc_test/doc_case_jinja", "warnings": sys.stderr}], indirect=True
)
def test_case_jinja(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert ">print<" in html
    assert ">&quot;this is my code&quot;<" in html
