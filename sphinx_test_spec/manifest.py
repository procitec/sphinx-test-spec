from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

TESTSPEC_MANIFEST_SCHEMA_VERSION = 1


class ManifestError(ValueError):
    """Raised when a test specification manifest is structurally invalid."""


def semantic_hash_payload(payload: dict[str, Any]) -> dict[str, Any]:
    document = payload.get("document", {})
    cases = []
    for case in payload.get("cases", []):
        cases.append(
            {
                "docname": case.get("docname"),
                "id": case.get("id"),
                "title": case.get("title"),
                "steps": [
                    {
                        "number": step.get("number"),
                        "action": step.get("action"),
                        "reaction": step.get("reaction"),
                    }
                    for step in case.get("steps", [])
                ],
            }
        )

    return {
        "schema_version": payload.get("schema_version"),
        "document": {
            "id": document.get("id"),
            "title": document.get("title"),
            "source": document.get("source"),
        },
        "namespace": payload.get("namespace", ""),
        "cases": cases,
    }


def calculate_spec_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        semantic_hash_payload(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def with_spec_hash(payload: dict[str, Any]) -> dict[str, Any]:
    content = deepcopy(payload)
    content.setdefault("document", {})["spec_hash"] = calculate_spec_hash(payload)
    return content


def validate_manifest(manifest: dict[str, Any]) -> None:
    schema_version = manifest.get("schema_version")
    if schema_version != TESTSPEC_MANIFEST_SCHEMA_VERSION:
        raise ManifestError(
            f"unsupported testspec manifest schema_version {schema_version!r}; "
            f"expected {TESTSPEC_MANIFEST_SCHEMA_VERSION}"
        )

    document = manifest.get("document")
    if not isinstance(document, dict):
        raise ManifestError("manifest is missing the 'document' object")

    expected_hash = document.get("spec_hash")
    if not isinstance(expected_hash, str) or not expected_hash:
        raise ManifestError("manifest is missing document.spec_hash")

    actual_hash = calculate_spec_hash(manifest)
    if actual_hash != expected_hash:
        raise ManifestError(
            "manifest spec_hash does not match the contained test specification: "
            f"expected {expected_hash}, calculated {actual_hash}"
        )

    cases = manifest.get("cases")
    if not isinstance(cases, list):
        raise ManifestError("manifest 'cases' must be a list")
