from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys


@pytest.mark.parametrize(
    "test_app", [{"buildername": "html", "srcdir": "doc_test/doc_role_action", "warnings": sys.stderr}], indirect=True
)
def test_doc_role_action(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert '<span class="pre">1.0<' in html
    assert 'class="reference internal" href="#test-action-1.ID_TEST_001"><code class="xref test test-action' in html
    assert '<span class="pre">1.1<' in html
    assert 'class="reference internal" href="#test-action-1.ID_TEST_002"><code class="xref test test-action' in html
