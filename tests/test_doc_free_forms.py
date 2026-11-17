import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "html", "srcdir": "doc_test/doc_free_forms", "warnings": sys.stderr}],
    indirect=True,
)
def test_free_choice_and_comment_fields(test_app):
    app = test_app
    app.build()

    html = Path(app.outdir, "index.html").read_text(encoding="utf-8")

    assert "Betriebssystem des Testsystems:" in html
    assert html.count('class="testspec-form-radio-option"') == 3
    assert html.count('type="radio"') == 3
    assert html.count('name="testspec_radio_operating-system_') == 3
    assert 'value="option_001"' in html
    assert 'value="option_002"' in html
    assert 'value="option_003"' in html
    assert "Ubuntu" in html
    assert "RedHat" in html
    assert "Windows" in html
    assert "testspec-form-radio-options" in html
    assert "flex: 1 1 0" in html

    assert "Allgemeine Anmerkungen zur Testdurchführung:" in html
    assert 'class="testspec-pdf-form testspec-form-comment-input"' in html
    assert 'name="testspec_comment_general-notes_' in html
    assert 'rows="5"' in html
