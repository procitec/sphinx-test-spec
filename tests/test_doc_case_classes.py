from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_case_classes", "warnings": sys.stderr}], indirect=True)
def test_case_classes(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert html.count('<tr class=') == 3
    assert html.count('<table class=') == 1

    assert '<table class="test-case-table' in html
    assert html.count('<tr class="test-action-row') == 2
    assert html.count('<td class="test-action">') == 2
    assert html.count('<td class="test-reaction">') == 2
    assert html.count('<td class="test-action-state">') == 2

    assert html.count('<section class="test-case-section"') == 1
    assert html.count('<thead class="test-case-table-head">') == 1

    assert '<div class="test-case-content docutils container">\n<p>This is free text before the table after the title</p>\n</div>' in html
