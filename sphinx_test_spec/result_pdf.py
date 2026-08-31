from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from sphinx_test_spec.manifest import ManifestError, validate_manifest
from sphinx_test_spec.result import ResultProcessingError, TestSpecResult, build_result

DEFAULT_MANIFEST_NAME = "testspec-manifest.json"


def _read_json_bytes(content: bytes, source: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResultProcessingError(f"cannot read JSON manifest from {source}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ResultProcessingError(f"manifest from {source} is not a JSON object")
    return parsed


def read_embedded_manifest(reader: PdfReader, manifest_name: str = DEFAULT_MANIFEST_NAME) -> dict[str, Any] | None:
    attachments = reader.attachments
    if manifest_name not in attachments:
        return None

    contents = attachments[manifest_name]
    if len(contents) != 1:
        raise ResultProcessingError(
            f"PDF contains {len(contents)} attachments named {manifest_name!r}; expected exactly one"
        )
    return _read_json_bytes(contents[0], f"PDF attachment {manifest_name!r}")


def read_external_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    try:
        content = manifest_path.read_bytes()
    except OSError as exc:
        raise ResultProcessingError(f"cannot read manifest {manifest_path}: {exc}") from exc
    return _read_json_bytes(content, str(manifest_path))


def select_manifest(
    reader: PdfReader,
    external_manifest: str | Path | None = None,
    manifest_name: str = DEFAULT_MANIFEST_NAME,
) -> dict[str, Any]:
    embedded = read_embedded_manifest(reader, manifest_name)
    external = read_external_manifest(external_manifest) if external_manifest is not None else None

    if embedded is None and external is None:
        raise ResultProcessingError(
            f"PDF has no embedded {manifest_name!r}; provide a manifest explicitly with --manifest"
        )

    for source, manifest in (("embedded", embedded), ("external", external)):
        if manifest is None:
            continue
        try:
            validate_manifest(manifest)
        except ManifestError as exc:
            raise ResultProcessingError(f"{source} manifest validation failed: {exc}") from exc

    if embedded is not None and external is not None:
        embedded_hash = embedded["document"]["spec_hash"]
        external_hash = external["document"]["spec_hash"]
        if embedded_hash != external_hash:
            raise ResultProcessingError(
                "embedded and external manifests describe different test specifications: "
                f"{embedded_hash} != {external_hash}"
            )

    if embedded is not None:
        return embedded
    assert external is not None
    return external


def _decode_radio_value(field: Any) -> str | None:
    raw_value = field.get("/V")
    if raw_value is None:
        return None

    value = str(raw_value)
    if value in {"", "/Off", "Off"}:
        return None

    normalized = value.lstrip("/")
    options = [str(option) for option in field.get("/Opt", [])]
    if normalized in options:
        return normalized

    # WeasyPrint represents radio button export values as /0, /1, /2 and
    # stores the semantic values in /Opt in the same order.
    if normalized.isdigit():
        index = int(normalized)
        if 0 <= index < len(options):
            return options[index]

    return normalized


def _decode_text_value(field: Any) -> str:
    raw_value = field.get("/V")
    if raw_value is None:
        return ""
    return str(raw_value).strip()


def _form_field_map(reader: PdfReader) -> dict[str, Any]:
    acro_form = reader.root_object.get("/AcroForm")
    if acro_form is None:
        return {}
    acro_form = acro_form.get_object()

    candidates: dict[str, list[Any]] = {}
    visited: set[int] = set()

    def visit(reference: Any) -> None:
        field = reference.get_object() if hasattr(reference, "get_object") else reference
        marker = id(field)
        if marker in visited:
            return
        visited.add(marker)

        name = field.get("/T")
        if name is not None:
            candidates.setdefault(str(name), []).append(field)

        for child in field.get("/Kids", []):
            visit(child)

    for field in acro_form.get("/Fields", []):
        visit(field)

    selected: dict[str, Any] = {}
    for name, fields in candidates.items():
        # For WeasyPrint radio groups, prefer the parent field because it owns
        # /V, /Opt and the complete widget list. Text fields are already leaf
        # fields and naturally win over widget-only children.
        selected[name] = max(
            fields,
            key=lambda field: (
                bool(field.get("/Kids")),
                str(field.get("/FT", "")) in {"/Btn", "/Tx"},
            ),
        )
    return selected


def extract_form_values(reader: PdfReader, manifest: dict[str, Any]) -> tuple[dict[str, str | None], dict[str, str]]:
    fields = _form_field_map(reader)
    result_values: dict[str, str | None] = {}
    comments: dict[str, str] = {}

    for case in manifest.get("cases", []):
        for step in case.get("steps", []):
            field_name = step.get("result_field")
            if not isinstance(field_name, str) or not field_name:
                continue
            field = fields.get(field_name)
            result_values[field_name] = _decode_radio_value(field) if field is not None else None

        comment_field = case.get("comment_field")
        if isinstance(comment_field, str) and comment_field:
            field = fields.get(comment_field)
            comments[comment_field] = _decode_text_value(field) if field is not None else ""

    return result_values, comments


def read_pdf_result(
    pdf_path: str | Path,
    execution_prefix: str = "",
    external_manifest: str | Path | None = None,
    manifest_name: str = DEFAULT_MANIFEST_NAME,
) -> TestSpecResult:
    path = Path(pdf_path)
    try:
        reader = PdfReader(path)
    except Exception as exc:
        raise ResultProcessingError(f"cannot read PDF {path}: {exc}") from exc

    if reader.is_encrypted:
        raise ResultProcessingError(f"PDF {path} is encrypted; decrypt it before result extraction")

    manifest = select_manifest(reader, external_manifest=external_manifest, manifest_name=manifest_name)
    values, comments = extract_form_values(reader, manifest)
    return build_result(manifest, values, comments, execution_prefix)
