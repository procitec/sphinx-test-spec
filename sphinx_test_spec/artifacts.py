from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any

from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

from sphinx_test_spec.manifest import (
    TESTSPEC_MANIFEST_SCHEMA_VERSION,
    with_spec_hash,
)

TESTSPEC_RESOURCES_FILENAME = "testspec-resources.json"
LEGACY_TESTSPEC_RESOURCES_FILENAME = "testspec.json"
TESTSPEC_MANIFEST_FILENAME = "testspec-manifest.json"


def _write_json(path: str, content: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=4, sort_keys=True)


def build_resources_content(app: Sphinx) -> dict[str, Any]:
    test_domain = app.env.get_domain("test")
    content: dict[str, Any] = {
        "project": app.config.project,
        "document": app.config.master_doc,
    }

    files = test_domain.data.get("files", {})
    if files:
        content["files"] = files

    return content


def write_testspec_resources(app: Sphinx, outdir: str) -> str:
    output = os.path.join(outdir, TESTSPEC_RESOURCES_FILENAME)
    _write_json(output, build_resources_content(app))

    legacy_output = os.path.join(outdir, LEGACY_TESTSPEC_RESOURCES_FILENAME)
    if os.path.isfile(legacy_output):
        os.remove(legacy_output)

    return output


def _qualified_id(namespace: str, case_id: str | None) -> str | None:
    if not case_id:
        return None

    parts = [part.strip(".") for part in (namespace, case_id) if part and part.strip(".")]
    return ".".join(parts)


def _validate_case_ids(cases: list[dict[str, Any]]) -> None:
    seen: dict[str, str] = {}
    for case in cases:
        case_id = case.get("id")
        if not case_id:
            continue

        location = case.get("docname", "<unknown>")
        if case_id in seen:
            raise ExtensionError(
                f"duplicate test:case id '{case_id}' in '{location}' and '{seen[case_id]}'"
            )
        seen[case_id] = location


def _manifest_payload(app: Sphinx) -> dict[str, Any]:
    test_domain = app.env.get_domain("test")
    namespace = app.config.testspec_namespace.strip(".")
    document_id = app.config.testspec_document_id or app.config.master_doc

    cases = deepcopy(test_domain.data.get("manifest_cases", []))
    cases.sort(key=lambda case: (case.get("docname", ""), case.get("id") or "", case.get("title", "")))
    _validate_case_ids(cases)

    for case in cases:
        case["qualified_id"] = _qualified_id(namespace, case.get("id"))

    return {
        "schema_version": TESTSPEC_MANIFEST_SCHEMA_VERSION,
        "document": {
            "id": document_id,
            "title": app.config.project,
            "source": app.config.master_doc,
        },
        "namespace": namespace,
        "result_mode": app.config.testspec_result_mode,
        "cases": cases,
    }



def build_manifest_content(app: Sphinx) -> dict[str, Any]:
    return with_spec_hash(_manifest_payload(app))


def write_testspec_manifest(app: Sphinx, outdir: str) -> str:
    output = os.path.join(outdir, TESTSPEC_MANIFEST_FILENAME)
    _write_json(output, build_manifest_content(app))
    return output
