import sys
from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "test_app", [{"buildername": "html", "srcdir": "doc_test/doc_role_file", "warnings": sys.stderr}], indirect=True
)
def test_doc_role_file(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    warning = app._warning
    warnings = warning.getvalue()

    assert "ERROR" not in warnings
    assert 2 == html.count("example.zvd")
    assert 2 == html.count("example.wav")
    assert 1 == html.count('<li class="test-filelist-item">example.zvd</li>')
    assert 1 == html.count('<li class="test-filelist-item">example.wav</li>')
