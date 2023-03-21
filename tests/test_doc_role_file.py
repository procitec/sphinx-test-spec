from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_role_file", "warnings": sys.stderr}], indirect=True)
def test_doc_role_file(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    warning = app._warning
    warnings = warning.getvalue()
    print(warnings)

    assert "ERROR" not in warnings

    assert 'example.wav' in html
