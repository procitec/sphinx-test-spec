from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    BooleanObject,
    DecodedStreamObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from sphinx_test_spec.pdf_forms import normalize_weasyprint_form_pdf


def _write_weasyprint_like_radio_pdf(
    path: Path,
    selected: int | None = None,
    field_name: str = "testspec_case_demo_step_001_result",
    options: tuple[str, ...] = ("passed", "failed", "na"),
) -> None:
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)

    group = DictionaryObject(
        {
            NameObject("/FT"): NameObject("/Btn"),
            NameObject("/Ff"): NumberObject((1 << 14) + (1 << 15)),
            NameObject("/T"): TextStringObject(field_name),
            NameObject("/V"): NameObject("/Off"),
            NameObject("/Kids"): ArrayObject(),
            NameObject("/Opt"): ArrayObject([TextStringObject(option) for option in options]),
        }
    )
    group_ref = writer._add_object(group)

    annotations = ArrayObject()
    for index in range(len(options)):
        checked_stream = DecodedStreamObject()
        checked_stream.set_data(b"raw-weasyprint-on-appearance")
        checked_stream[NameObject("/Type")] = NameObject("/XObject")
        checked_stream[NameObject("/Subtype")] = NameObject("/Form")
        checked_stream[NameObject("/BBox")] = ArrayObject(
            [FloatObject(0), FloatObject(0), FloatObject(10), FloatObject(10)]
        )
        checked_ref = writer._add_object(checked_stream)
        normal = DictionaryObject({NameObject(f"/{index}"): checked_ref})
        widget = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/Rect"): ArrayObject(
                    [
                        FloatObject(10 + index * 20),
                        FloatObject(30),
                        FloatObject(20 + index * 20),
                        FloatObject(20),
                    ]
                ),
                NameObject("/P"): page.indirect_reference,
                NameObject("/F"): NumberObject(4),
                NameObject("/T"): TextStringObject(field_name),
                NameObject("/FT"): NameObject("/Btn"),
                NameObject("/AS"): NameObject(f"/{index}") if selected == index else NameObject("/Off"),
                NameObject("/AP"): DictionaryObject({NameObject("/N"): normal}),
                NameObject("/Parent"): group_ref,
            }
        )
        widget_ref = writer._add_object(widget)
        group[NameObject("/Kids")].append(widget_ref)
        annotations.append(widget_ref)

    page[NameObject("/Annots")] = annotations
    acro_form = DictionaryObject(
        {
            NameObject("/Fields"): ArrayObject([group_ref, *annotations]),
            NameObject("/NeedAppearances"): BooleanObject(True),
        }
    )
    writer.root_object[NameObject("/AcroForm")] = writer._add_object(acro_form)

    with path.open("wb") as file:
        writer.write(file)


def test_normalize_weasyprint_radio_structure_and_appearances(tmp_path):
    source = tmp_path / "form.pdf"
    _write_weasyprint_like_radio_pdf(source)

    assert normalize_weasyprint_form_pdf(source) == 1

    reader = PdfReader(source)
    acro_form = reader.root_object["/AcroForm"].get_object()
    assert acro_form["/NeedAppearances"].value is False
    assert len(acro_form["/Fields"]) == 1

    group = acro_form["/Fields"][0].get_object()
    assert group["/V"] == "/Off"
    assert group["/DV"] == "/Off"
    assert "/Opt" not in group
    assert len(group["/Kids"]) == 3

    expected_states = ["/passed", "/failed", "/na"]
    for child_ref, expected_state in zip(group["/Kids"], expected_states, strict=True):
        child = child_ref.get_object()
        assert "/T" not in child
        assert "/FT" not in child
        assert "/V" not in child
        assert "/DA" not in child
        assert "/MK" not in child
        assert child["/F"] & 4
        assert child["/AS"] == "/Off"

        appearances = child["/AP"]["/N"]
        assert set(appearances.keys()) == {"/Off", expected_state}
        off_data = appearances["/Off"].get_object().get_data()
        on_data = appearances[expected_state].get_object().get_data()
        assert off_data
        assert on_data
        assert b"\nS\n" in off_data
        assert b"\nf\n" not in off_data
        assert b"\nS\n" in on_data
        assert b"\nf\n" in on_data


def test_normalize_recovers_selected_widget_state(tmp_path):
    source = tmp_path / "saved.pdf"
    _write_weasyprint_like_radio_pdf(source, selected=1)

    normalize_weasyprint_form_pdf(source)

    reader = PdfReader(source)
    group = reader.root_object["/AcroForm"]["/Fields"][0].get_object()
    assert group["/V"] == "/failed"
    assert [str(child.get_object()["/AS"]) for child in group["/Kids"]] == [
        "/Off",
        "/failed",
        "/Off",
    ]


def test_normalized_radio_group_roundtrip_keeps_single_selection(tmp_path):
    source = tmp_path / "roundtrip.pdf"
    _write_weasyprint_like_radio_pdf(source)
    normalize_weasyprint_form_pdf(source)

    reader = PdfReader(source)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.update_page_form_field_values(
        None,
        {"testspec_case_demo_step_001_result": "/failed"},
        auto_regenerate=False,
    )
    saved = tmp_path / "roundtrip-saved.pdf"
    with saved.open("wb") as file:
        writer.write(file)

    reopened = PdfReader(saved)
    group = reopened.root_object["/AcroForm"]["/Fields"][0].get_object()
    assert group["/V"] == "/failed"
    assert [str(child.get_object()["/AS"]) for child in group["/Kids"]] == [
        "/Off",
        "/failed",
        "/Off",
    ]


def test_normalize_free_radio_group(tmp_path):
    source = tmp_path / "free-radio.pdf"
    _write_weasyprint_like_radio_pdf(
        source,
        field_name="testspec_radio_operating-system_deadbeef",
        options=("option_001", "option_002", "option_003"),
    )

    assert normalize_weasyprint_form_pdf(source) == 1

    reader = PdfReader(source)
    acro_form = reader.root_object["/AcroForm"].get_object()
    group = acro_form["/Fields"][0].get_object()
    assert group["/T"] == "testspec_radio_operating-system_deadbeef"
    assert "/Opt" not in group
    assert group["/V"] == "/Off"

    expected_states = ["/option_001", "/option_002", "/option_003"]
    for child_ref, expected_state in zip(group["/Kids"], expected_states, strict=True):
        child = child_ref.get_object()
        assert child["/AS"] == "/Off"
        assert set(child["/AP"]["/N"].keys()) == {"/Off", expected_state}
