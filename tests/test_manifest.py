from copy import deepcopy

import pytest

from sphinx_test_spec.manifest import ManifestError, validate_manifest, with_spec_hash


def _manifest():
    return {
        "schema_version": 1,
        "document": {"id": "manual", "title": "Manual", "source": "index"},
        "namespace": "category.appname",
        "cases": [
            {
                "docname": "index",
                "id": "startup",
                "title": "Startup",
                "steps": [{"number": 1, "action": "Start", "reaction": "Runs"}],
            }
        ],
    }


def test_manifest_hash_ignores_result_mapping_fields():
    manifest = with_spec_hash(_manifest())
    changed = deepcopy(manifest)
    changed["cases"][0]["steps"][0]["result_field"] = "technical-field"
    validate_manifest(changed)


def test_manifest_hash_detects_semantic_changes():
    manifest = with_spec_hash(_manifest())
    manifest["cases"][0]["steps"][0]["reaction"] = "Different"
    with pytest.raises(ManifestError, match="spec_hash"):
        validate_manifest(manifest)
