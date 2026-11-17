from sphinx_test_spec.forms import result_controls_html, result_header_html


def test_result_labels_are_rendered_only_in_header():
    labels = {"passed": "✓", "failed": "✗", "na": "–"}

    header = result_header_html(labels)
    controls = result_controls_html("case_step_result", labels)

    assert "✓" in header
    assert "✗" in header
    assert "–" in header
    assert ">✓<" not in controls
    assert ">✗<" not in controls
    assert ">–<" not in controls
    assert controls.count('type="radio"') == 3
    assert 'aria-label="passed"' in controls
    assert 'aria-label="failed"' in controls
    assert 'aria-label="na"' in controls


def test_result_header_can_have_optional_caption():
    header = result_header_html(caption="Result")

    assert "testspec-result-header-caption" in header
    assert ">Result<" in header
    assert "✓" in header
    assert "✗" in header
    assert "–" in header


def test_result_controls_force_horizontal_non_wrapping_layout():
    controls = result_controls_html("case_step_result")

    assert "display: flex" in controls
    assert "flex-wrap: nowrap" in controls
    assert controls.count("display: inline-flex") == 3
    assert controls.count("flex: 1 1 0") == 3
