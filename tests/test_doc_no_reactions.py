from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys

@pytest.mark.parametrize("test_app", [{"buildername": "html", "srcdir": "doc_test/doc_no_reactions", "warnings": sys.stderr}], indirect=True)
def test_doc_no_reactions(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()

    assert '<h2>Summarize and Clear values in calculator' in html

    assert '<tr class="test-action-row row-even"><td class="test-action-id">1.0</td>' in html
    assert '<td class="test-action"><p>Type ‘2+2’ into your systems calculator app and press ‘&lt;enter&gt;’.' in html
    assert 'Clear the results, e.g. by typing ‘&lt;C&gt;’ or another button for clearing the results in your app' in html
    assert html.count('<tr class=') == 3
    assert html.count('<table class=') == 1
