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
        # WeasyPrint paints a native circle slightly outside the original
        # 10 x 10 pt widget. Expanding the widget allows its opaque backing
        # to hide that circle rather than drawing a double outline.
        rect = child["/Rect"]
        assert round(float(rect[2]) - float(rect[0]), 3) == 13.2
        assert round(float(rect[3]) - float(rect[1]), 3) == 13.2

        appearances = child["/AP"]["/N"]
        assert set(appearances.keys()) == {"/Off", expected_state}
        off_data = appearances["/Off"].get_object().get_data()
        on_data = appearances[expected_state].get_object().get_data()
        # Both states must include the outer circle. A transparent /Off
        # appearance makes the input outline disappear in some PDF viewers.
        assert b"1 1 1 rg" in off_data  # Background masks WeasyPrint's native outline.
        assert b"0 0 0 RG" in off_data
        assert off_data.count(b"\nS\n") == 1
        assert on_data.count(b"\nS\n") == 1
        assert off_data.count(b"\nf\n") == 1  # White circle only.
        assert on_data.count(b"\nf\n") == 2  # White circle and selected dot.
        assert on_data.startswith(off_data[: off_data.index(b"\nQ\n")])


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
        # test:choice uses the same complete visible outline as the protocol
        # fields, including in the deselected state.
        assert b"\nS\n" in child["/AP"]["/N"]["/Off"].get_object().get_data()
        assert b"\nS\n" in child["/AP"]["/N"][expected_state].get_object().get_data()


def test_normalize_radio_twice_does_not_enlarge_widgets_again(tmp_path):
    source = tmp_path / "form-twice.pdf"
    _write_weasyprint_like_radio_pdf(source)

    assert normalize_weasyprint_form_pdf(source) == 1
    first = PdfReader(source)
    group = first.root_object["/AcroForm"]["/Fields"][0].get_object()
    rects = [list(child.get_object()["/Rect"]) for child in group["/Kids"]]

    assert normalize_weasyprint_form_pdf(source) == 1
    second = PdfReader(source)
    group = second.root_object["/AcroForm"]["/Fields"][0].get_object()
    assert [list(child.get_object()["/Rect"]) for child in group["/Kids"]] == rects


def test_normalize_free_and_result_radios_share_border_appearance(tmp_path):
    # The protocol and test:choice fields must use the same visual outline.
    result_pdf = tmp_path / "protocol.pdf"
    choice_pdf = tmp_path / "choice.pdf"
    _write_weasyprint_like_radio_pdf(result_pdf)
    _write_weasyprint_like_radio_pdf(
        choice_pdf,
        field_name="testspec_radio_choice_123",
        options=("option_001", "option_002", "option_003"),
    )
    normalize_weasyprint_form_pdf(result_pdf)
    normalize_weasyprint_form_pdf(choice_pdf)

    def off_stream(path):
        group = PdfReader(path).root_object["/AcroForm"]["/Fields"][0].get_object()
        widget = group["/Kids"][0].get_object()
        return widget["/AP"]["/N"]["/Off"].get_object().get_data()

    assert off_stream(result_pdf) == off_stream(choice_pdf)
