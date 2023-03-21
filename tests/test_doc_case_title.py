from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys


@pytest.mark.parametrize(
    "test_app", [{"buildername": "html", "srcdir": "doc_test/doc_case_title", "warnings": sys.stderr}], indirect=True
)
def test_case_title(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert html.count("<tr class=") == 4
    assert html.count("<table class=") == 2

    assert 'See if this code <code class="code' in html
    assert '<span class="pre">calculator</span></code>' in html
    assert "See if this section <" in html
