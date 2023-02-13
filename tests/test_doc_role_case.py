from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_role_case", "warnings": sys.stderr}], indirect=True)
def test_doc_role_case(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert 'As you can read in <a class="reference internal" href="#test-case-Summarize and Clear values in calculator"' in html
