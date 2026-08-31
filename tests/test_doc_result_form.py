import json
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "html", "srcdir": "doc_test/doc_result_form", "warnings": sys.stderr}],
    indirect=True,
)
def test_result_form_and_manifest(test_app):
    app = test_app
    app.build()

    html = Path(app.outdir, "index.html").read_text(encoding="utf-8")
    manifest = json.loads(Path(app.outdir, "testspec-manifest.json").read_text(encoding="utf-8"))

    assert '<link rel="attachment" href="testspec-manifest.json"' in html
    assert html.count('type="radio"') == 6
    assert html.count('value="passed"') == 2
    assert html.count('value="failed"') == 2
    assert html.count('value="na"') == 2
    assert html.count('testspec-case-comment-input') == 1
    assert "testspec-result-header-labels" in html
    assert "testspec-result-options" in html
    assert "testspec-result-passed" in html
    assert "testspec-result-failed" in html
    assert "testspec-result-na" in html
    assert html.count("✓") == 1
    assert html.count("✗") == 1
    assert html.count("–") == 1
    assert html.count('aria-label="passed"') == 2
    assert html.count('aria-label="failed"') == 2
    assert html.count('aria-label="na"') == 2
    assert 'Anmerkung:' in html
    assert 'href="#test-case-startup"' in html

    assert manifest["schema_version"] == 1
    assert manifest["document"]["id"] == "application-manual-test"
    assert manifest["document"]["spec_hash"].startswith("sha256:")
    assert manifest["namespace"] == "category.appname"
    assert len(manifest["cases"]) == 1

    case = manifest["cases"][0]
    assert case["id"] == "startup"
    assert case["qualified_id"] == "category.appname.startup"
    assert case["field_key"].startswith("startup_")
    assert case["comment_field"] == f"testspec_case_{case['field_key']}_comment"
    assert len(case["steps"]) == 2
    assert case["steps"][0]["number"] == 1
    assert case["steps"][0]["result_field"] == f"testspec_case_{case['field_key']}_step_001_result"
    assert case["steps"][1]["number"] == 2
    assert case["steps"][1]["result_field"] == f"testspec_case_{case['field_key']}_step_002_result"
