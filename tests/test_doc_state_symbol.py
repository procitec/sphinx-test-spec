from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_state_symbol", "warnings": sys.stderr}], indirect=True)
def test_doc_state_symbol(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert html.count('<tr class=') == 3
    assert html.count('<table class=') == 1

    assert "☐" in html
    assert html.count('<td class="test-action-state">☐</td>') == 2
