from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_role_action_invalid", "warnings": sys.stderr}], indirect=True)
def test_doc_role_action_invalid(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    # this is NOT intended to be in the output, we do not want to be able to cross reference the nodes over cases

    assert 'class="reference internal" href="#test-action-1.ID_TEST_001"><code class="xref test test-action' in html
