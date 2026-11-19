import json
from pathlib import Path

import pytest

from sphinx_test_spec.manifest import validate_manifest


@pytest.mark.parametrize(
    "test_app",
    [
        {"buildername": "html", "srcdir": "doc_test/doc_manifest_substitutions"},
        {"buildername": "testspec", "srcdir": "doc_test/doc_manifest_substitutions"},
    ],
    indirect=True,
)
def test_manifest_contains_step_ids_and_resolved_substitutions(test_app):
    app = test_app
    app.build()

    assert Path(app.outdir, "testspec-resources.json").is_file()
    manifest = json.loads(Path(app.outdir, "testspec-manifest.json").read_text(encoding="utf-8"))
    validate_manifest(manifest)

    first, second = manifest["cases"]
    assert first["id"] == "CASE_100"
    assert first["title"] == "Verify CamelBrand"
    assert first["steps"][0]["action"] == "Start CamelBrand."
    assert first["steps"][0]["reaction"] == "CamelBrand shows the Ready state."
    assert first["steps"][0]["action_id"] == "ACTION_START"
    assert first["steps"][0]["reaction_id"] == "REACTION_STARTED"

    assert first["steps"][1]["action"] == "Stop CamelBrand."
    assert first["steps"][1]["reaction"] == "CamelBrand is stopped."
    assert "action_id" not in first["steps"][1]
    assert "reaction_id" not in first["steps"][1]

    assert second["id"] == "CASE_200"
    assert second["steps"][0]["action_id"] == "ACTION_START"
    assert second["steps"][0]["reaction_id"] == "REACTION_STARTED"
    assert second["steps"][1]["action_id"] == "ACTION_ONLY"
    assert "reaction_id" not in second["steps"][1]
    assert "action_id" not in second["steps"][2]
    assert second["steps"][2]["reaction_id"] == "REACTION_ONLY"
    assert "|branding_camel_name|" not in json.dumps(manifest)

    if app.builder.name == "html":
        html = Path(app.outdir, "index.html").read_text(encoding="utf-8")
        assert "Start CamelBrand." in html
        assert "CamelBrand shows the" in html
    else:
        assert not Path(app.outdir, "index.html").exists()
