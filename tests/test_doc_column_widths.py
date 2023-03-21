from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys


@pytest.mark.parametrize(
    "test_app", [{"buildername": "html", "srcdir": "doc_test/doc_column_widths", "warnings": sys.stderr}], indirect=True
)
def test_doc_column_widths(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert "<colgroup>" in html
    assert 2 == html.count('<col style="width: 10.0%" />')
    assert 2 == html.count('<col style="width: 40.0%" />')
