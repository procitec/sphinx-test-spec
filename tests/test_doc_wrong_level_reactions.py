from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_wrong_level_reactions", "warnings": sys.stderr}], indirect=True)
def test_doc_wrong_levels_reactions(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert 'The calculator sums and shows you ‘4’ as result.' not in html
    assert 'The calculator does show ‘0‘ or shows nothing' not in html

    assert html.count('<tr class=') == 1
    assert html.count('<table class=') == 1
