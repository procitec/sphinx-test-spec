from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_case_content", "warnings": sys.stderr}], indirect=True)
def test_case_content(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert html.count('<tr class=') == 3
    assert html.count('<table class=') == 1

    assert "This is free text before the table after the title" in html
    assert "<tbody>\n<p>This is free text before the table after the title</p>" not in html

