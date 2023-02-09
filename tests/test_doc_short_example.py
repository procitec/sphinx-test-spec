from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_short_example", "warnings": sys.stderr}], indirect=True)
def test_doc_short_example(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert "Adding numbers in calculator" in html

    assert "into your systems calculator app and press" in html
