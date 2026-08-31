from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    BooleanObject,
    DecodedStreamObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
)

from sphinx_test_spec.forms import RESULT_VALUES


class PdfFormProcessingError(ValueError):
    """Raised when a generated PDF form cannot be normalized safely."""


def _as_object(value: Any) -> Any:
    return value.get_object() if hasattr(value, "get_object") else value


def _normal_appearances(widget: DictionaryObject) -> DictionaryObject | None:
    appearance = _as_object(widget.get("/AP"))
    if not isinstance(appearance, DictionaryObject):
        return None
    normal = _as_object(appearance.get("/N"))
    return normal if isinstance(normal, DictionaryObject) else None


def _appearance_size(widget: DictionaryObject) -> tuple[float, float]:
    normal = _normal_appearances(widget)
    if normal is not None:
        for stream_ref in normal.values():
            stream = _as_object(stream_ref)
            bbox = stream.get("/BBox") if isinstance(stream, DictionaryObject) else None
            if bbox is not None and len(bbox) == 4:
                width = abs(float(bbox[2]) - float(bbox[0]))
                height = abs(float(bbox[3]) - float(bbox[1]))
                if width > 0 and height > 0:
                    return width, height

    rect = widget.get("/Rect")
    if rect is not None and len(rect) == 4:
        width = abs(float(rect[2]) - float(rect[0]))
        height = abs(float(rect[3]) - float(rect[1]))
        if width > 0 and height > 0:
            return width, height

    return 8.0, 8.0


def _circle_path(cx: float, cy: float, radius: float) -> str:
    # Four cubic Bezier curves approximating a circle.
    kappa = 0.5522847498
    kr = radius * kappa
    return "\n".join(
        (
            f"{cx + radius:.3f} {cy:.3f} m",
            f"{cx + radius:.3f} {cy + kr:.3f} {cx + kr:.3f} {cy + radius:.3f} {cx:.3f} {cy + radius:.3f} c",
            f"{cx - kr:.3f} {cy + radius:.3f} {cx - radius:.3f} {cy + kr:.3f} {cx - radius:.3f} {cy:.3f} c",
            f"{cx - radius:.3f} {cy - kr:.3f} {cx - kr:.3f} {cy - radius:.3f} {cx:.3f} {cy - radius:.3f} c",
            f"{cx + kr:.3f} {cy - radius:.3f} {cx + radius:.3f} {cy - kr:.3f} {cx + radius:.3f} {cy:.3f} c",
        )
    )


def _radio_appearance_stream(width: float, height: float, selected: bool) -> DecodedStreamObject:
    size = min(width, height)
    cx = width / 2.0
    cy = height / 2.0
    line_width = max(0.45, size * 0.075)
    outer_radius = max(0.5, size * 0.36)
    inner_radius = max(0.3, size * 0.16)

    commands = [
        "q",
        "0 0 0 RG",
        "0 0 0 rg",
        f"{line_width:.3f} w",
        _circle_path(cx, cy, outer_radius),
        "S",
    ]
    if selected:
        commands.extend((_circle_path(cx, cy, inner_radius), "f"))
    commands.append("Q")

    stream = DecodedStreamObject()
    stream.set_data(("\n".join(commands) + "\n").encode("ascii"))
    stream[NameObject("/Type")] = NameObject("/XObject")
    stream[NameObject("/Subtype")] = NameObject("/Form")
    stream[NameObject("/FormType")] = NumberObject(1)
    stream[NameObject("/BBox")] = ArrayObject(
        [FloatObject(0), FloatObject(0), FloatObject(width), FloatObject(height)]
    )
    stream[NameObject("/Resources")] = DictionaryObject()
    return stream


def _semantic_radio_state(
    raw_state: Any,
    options: list[str],
    states: list[str],
) -> str | None:
    if raw_state is None:
        return None

    value = str(raw_state).lstrip("/")
    if not value or value == "Off":
        return None
    if value in states:
        return value
    if value.isdigit():
        index = int(value)
        return states[index] if 0 <= index < len(states) else None
    if value in options:
        index = options.index(value)
        return states[index] if index < len(states) else None
    return None


def _selected_radio_state(group: DictionaryObject, states: list[str]) -> str | None:
    options = [str(option).lstrip("/") for option in group.get("/Opt", [])]
    selected = _semantic_radio_state(group.get("/V"), options, states)
    if selected is not None:
        return selected

    child_states: list[str] = []
    for child_ref in group.get("/Kids", []):
        child = _as_object(child_ref)
        state = _semantic_radio_state(child.get("/AS"), options, states)
        if state is not None:
            child_states.append(state)
    return child_states[0] if len(set(child_states)) == 1 else None


def _set_widget_appearances(
    writer: PdfWriter,
    widget: DictionaryObject,
    state: str,
    selected_state: str | None,
) -> None:
    width, height = _appearance_size(widget)
    off_ref = writer._add_object(_radio_appearance_stream(width, height, selected=False))
    on_ref = writer._add_object(_radio_appearance_stream(width, height, selected=True))

    normal = DictionaryObject(
        {
            NameObject("/Off"): off_ref,
            NameObject(f"/{state}"): on_ref,
        }
    )
    widget[NameObject("/AP")] = DictionaryObject({NameObject("/N"): normal})
    widget[NameObject("/AS")] = NameObject(f"/{state}") if selected_state == state else NameObject("/Off")

    # The parent owns all field metadata. Kids are widget annotations only.
    for key in ("/T", "/TU", "/FT", "/Ff", "/V", "/DV", "/Opt", "/DA", "/MK"):
        if key in widget:
            del widget[key]

    # Keep the widgets printable in all readers.
    widget[NameObject("/F")] = NumberObject(int(widget.get("/F", 0)) | 4)


def _normalize_radio_group(
    writer: PdfWriter,
    group: DictionaryObject,
    states: list[str],
) -> None:
    selected_state = _selected_radio_state(group, states)
    kids = list(group.get("/Kids", []))

    for index, child_ref in enumerate(kids):
        child = _as_object(child_ref)
        if not isinstance(child, DictionaryObject):
            continue
        state = states[index] if index < len(states) else f"option_{index + 1:03d}"
        _set_widget_appearances(writer, child, state, selected_state)

    # A conventional radio group uses the widget appearance-state name as the
    # export value. /Opt is not needed and causes viewer-specific interpretation
    # together with WeasyPrint's numeric /0, /1, /2 states.
    if "/Opt" in group:
        del group["/Opt"]
    group[NameObject("/V")] = (
        NameObject(f"/{selected_state}") if selected_state else NameObject("/Off")
    )
    group[NameObject("/DV")] = NameObject("/Off")


def normalize_weasyprint_form_writer(writer: PdfWriter) -> int:
    """Normalize test-spec radio groups in a cloned WeasyPrint PDF."""
    acro_form_ref = writer.root_object.get("/AcroForm")
    if acro_form_ref is None:
        return 0
    acro_form = _as_object(acro_form_ref)
    fields = acro_form.get("/Fields", [])

    root_fields = ArrayObject()
    radio_groups: list[tuple[DictionaryObject, list[str]]] = []
    for field_ref in fields:
        field = _as_object(field_ref)
        # WeasyPrint also places widget kids in /Fields. Keep only actual root
        # fields; the kids remain reachable through their parent's /Kids.
        if field.get("/Parent") is not None:
            continue
        root_fields.append(field_ref)

        flags = int(field.get("/Ff", 0))
        field_name = str(field.get("/T", ""))
        is_radio = str(field.get("/FT", "")) == "/Btn" and bool(flags & (1 << 15))
        kids = list(field.get("/Kids", []))
        if not is_radio or not kids:
            continue

        is_testspec_result = field_name.startswith("testspec_case_") and field_name.endswith("_result")
        is_free_radio = field_name.startswith("testspec_radio_")
        if is_testspec_result:
            states = list(RESULT_VALUES)
        elif is_free_radio:
            options = [str(option).lstrip("/") for option in field.get("/Opt", [])]
            states = [
                options[index] if index < len(options) and options[index] else f"option_{index + 1:03d}"
                for index in range(len(kids))
            ]
        else:
            continue
        radio_groups.append((field, states))

    acro_form[NameObject("/Fields")] = root_fields
    for group, states in radio_groups:
        _normalize_radio_group(writer, group, states)

    if radio_groups:
        # We provide complete off/on appearance streams. Readers must not
        # regenerate them, otherwise live display/printing becomes viewer-specific.
        acro_form[NameObject("/NeedAppearances")] = BooleanObject(False)
    return len(radio_groups)


def normalize_weasyprint_form_pdf(
    pdf_path: str | Path,
    output_path: str | Path | None = None,
) -> int:
    """Normalize test-spec radio groups after WeasyPrint generated the PDF."""
    source = Path(pdf_path)
    target = Path(output_path) if output_path is not None else source

    try:
        reader = PdfReader(source)
    except Exception as exc:
        raise PdfFormProcessingError(f"cannot read PDF {source}: {exc}") from exc

    if reader.is_encrypted:
        raise PdfFormProcessingError(f"PDF {source} is encrypted and cannot be normalized")

    try:
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        group_count = normalize_weasyprint_form_writer(writer)
        if group_count == 0 and target == source:
            return 0

        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = source.with_name(f".{source.name}.testspec.tmp") if target == source else target
        with temporary.open("wb") as file:
            writer.write(file)
        if target == source:
            temporary.replace(source)
        return group_count
    except PdfFormProcessingError:
        raise
    except Exception as exc:
        raise PdfFormProcessingError(f"cannot normalize PDF {source}: {exc}") from exc
