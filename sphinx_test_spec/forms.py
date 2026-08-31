from __future__ import annotations

import hashlib
import re
from html import escape
from typing import Mapping

RESULT_VALUES = ("passed", "failed", "na")
DEFAULT_RESULT_LABELS = {
    "passed": "✓",
    "failed": "✗",
    "na": "–",
}


def case_field_key(case_id: str | None, docname: str, case_number: int) -> str:
    if case_id:
        source = case_id
        readable = re.sub(r"[^A-Za-z0-9_-]+", "_", case_id).strip("_") or "case"
    else:
        source = f"{docname}:{case_number}"
        readable = f"case_{case_number:03d}"

    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:8]
    return f"{readable}_{digest}"


def free_field_key(field_id: str, docname: str = "") -> str:
    """Return a stable, PDF-safe key for a free form field."""
    readable = re.sub(r"[^A-Za-z0-9_-]+", "_", field_id).strip("_") or "field"
    source = f"{docname}:{field_id}" if docname else field_id
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:8]
    return f"{readable}_{digest}"


def free_radio_field_name(field_id: str, docname: str = "") -> str:
    return f"testspec_radio_{free_field_key(field_id, docname)}"


def free_comment_field_name(field_id: str, docname: str = "") -> str:
    return f"testspec_comment_{free_field_key(field_id, docname)}"


def result_field_name(case_key: str, step_number: int) -> str:
    return f"testspec_case_{case_key}_step_{step_number:03d}_result"


def comment_field_name(case_key: str) -> str:
    return f"testspec_case_{case_key}_comment"


def normalize_result_labels(labels: Mapping[str, str] | None) -> dict[str, str]:
    normalized = dict(DEFAULT_RESULT_LABELS)
    if labels:
        normalized.update({key: str(value) for key, value in labels.items() if key in RESULT_VALUES})
    return normalized


def _result_group_style() -> str:
    return (
        "display: flex; flex-wrap: nowrap; width: 100%; "
        "align-items: center; justify-content: center; white-space: nowrap;"
    )


def _result_item_style() -> str:
    return (
        "display: inline-flex; flex: 1 1 0; min-width: 0; "
        "align-items: center; justify-content: center; margin: 0; padding: 0; white-space: nowrap;"
    )


def result_header_html(labels: Mapping[str, str] | None = None, caption: str = "") -> str:
    display_labels = normalize_result_labels(labels)
    items = []
    for value in RESULT_VALUES:
        label = escape(display_labels[value])
        items.append(
            f'<span class="testspec-result-header-option testspec-result-{value}" '
            f'title="{value}" style="{_result_item_style()}">{label}</span>'
        )

    group = (
        f'<span class="testspec-result-header-labels" style="{_result_group_style()}">'
        + "".join(items)
        + "</span>"
    )
    if not caption:
        return group

    return (
        '<span class="testspec-result-header" '
        'style="display: flex; flex-wrap: nowrap; align-items: center; white-space: nowrap;">'
        f'<span class="testspec-result-header-caption" style="margin-right: 0.35em;">{escape(caption)}</span>'
        f"{group}</span>"
    )


def result_controls_html(field_name: str, labels: Mapping[str, str] | None = None) -> str:
    escaped_name = escape(field_name, quote=True)
    controls = []
    for value in RESULT_VALUES:
        # Visible result labels are rendered once in the table header. Keep
        # per-widget metadata semantic and ASCII-only so the decorative
        # symbols are not repeated in every action row.
        semantic_label = escape(value, quote=True)
        controls.append(
            f'<label class="testspec-result-option testspec-result-{value}" title="{semantic_label}" '
            f'style="{_result_item_style()}">'
            f'<input class="testspec-pdf-form" type="radio" name="{escaped_name}" '
            f'value="{value}" aria-label="{semantic_label}" '
            'style="appearance: auto; display: inline-block; flex: 0 0 auto; margin: 0; padding: 0;">'
            "</label>"
        )
    return (
        f'<span class="testspec-result-options" style="{_result_group_style()}">'
        + "".join(controls)
        + "</span>"
    )


def comment_control_html(field_name: str, label: str = "Comment") -> str:
    escaped_name = escape(field_name, quote=True)
    escaped_label = escape(label)
    return (
        '<div class="testspec-case-comment" style="margin-top: 0.5em;">'
        f"<label>{escaped_label}: "
        f'<input class="testspec-pdf-form testspec-case-comment-input" type="text" name="{escaped_name}" '
        'style="appearance: auto; width: 80%;">'
        "</label>"
        "</div>"
    )


def free_radio_control_html(
    label: str,
    field_name: str,
    options: list[str],
    extra_class: str = "",
) -> str:
    """Render a generic, single-line radio group for HTML/WeasyPrint."""
    escaped_name = escape(field_name, quote=True)
    escaped_label = escape(label)
    wrapper_classes = "testspec-form-radio"
    if extra_class.strip():
        wrapper_classes += " " + escape(extra_class.strip(), quote=True)

    controls: list[str] = []
    for index, option in enumerate(options, start=1):
        option_label = escape(option)
        option_value = f"option_{index:03d}"
        controls.append(
            '<label class="testspec-form-radio-option" '
            'style="display: inline-flex; flex: 1 1 0; min-width: 0; align-items: center; '
            'justify-content: center; gap: 0.3em; margin: 0; padding: 0 0.2em;">'
            f'<input class="testspec-pdf-form" type="radio" name="{escaped_name}" '
            f'value="{option_value}" aria-label="{escape(option, quote=True)}" '
            'style="appearance: auto; display: inline-block; flex: 0 0 auto; margin: 0; padding: 0;">'
            f'<span class="testspec-form-radio-label">{option_label}</span>'
            '</label>'
        )

    return (
        f'<div class="{wrapper_classes}" style="margin: 0.6em 0;">'
        f'<div class="testspec-form-label" style="margin-bottom: 0.25em;">{escaped_label}:</div>'
        '<div class="testspec-form-radio-options" '
        'style="display: flex; flex-wrap: nowrap; width: 100%; align-items: center; '
        'justify-content: space-between;">'
        + "".join(controls)
        + "</div></div>"
    )


def free_comment_control_html(
    label: str,
    field_name: str,
    rows: int = 4,
    extra_class: str = "",
) -> str:
    """Render a generic multiline comment field for HTML/WeasyPrint."""
    escaped_name = escape(field_name, quote=True)
    escaped_label = escape(label)
    wrapper_classes = "testspec-form-comment"
    if extra_class.strip():
        wrapper_classes += " " + escape(extra_class.strip(), quote=True)

    safe_rows = max(1, int(rows))
    return (
        f'<div class="{wrapper_classes}" style="margin: 0.6em 0;">'
        f'<label class="testspec-form-label" for="{escaped_name}">{escaped_label}:</label>'
        f'<textarea class="testspec-pdf-form testspec-form-comment-input" id="{escaped_name}" '
        f'name="{escaped_name}" rows="{safe_rows}" '
        'style="appearance: auto; display: block; width: 100%; box-sizing: border-box; '
        'margin-top: 0.25em; font-family: inherit; font-size: inherit;"></textarea>'
        '</div>'
    )
