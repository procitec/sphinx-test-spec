from sphinx_test_spec.result_pdf import _decode_radio_value


def test_decode_weasyprint_radio_index():
    field = {"/V": "/1", "/Opt": ["passed", "failed", "na"]}
    assert _decode_radio_value(field) == "failed"


def test_decode_semantic_radio_value():
    field = {"/V": "/passed", "/Opt": ["passed", "failed", "na"]}
    assert _decode_radio_value(field) == "passed"


def test_decode_empty_radio_value():
    assert _decode_radio_value({"/V": "/Off", "/Opt": ["passed", "failed", "na"]}) is None
