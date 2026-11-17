from sphinx_test_spec.forms import (
    free_comment_control_html,
    free_comment_field_name,
    free_radio_control_html,
    free_radio_field_name,
)


def test_free_radio_control_uses_one_group_and_equal_width_items():
    field_name = free_radio_field_name("operating-system", "index")
    html = free_radio_control_html(
        "Betriebssystem",
        field_name,
        ["Ubuntu", "RedHat", "Windows"],
    )

    assert "Betriebssystem:" in html
    assert html.count('type="radio"') == 3
    assert html.count(f'name="{field_name}"') == 3
    assert html.count("flex: 1 1 0") == 3
    assert 'value="option_001"' in html
    assert 'value="option_002"' in html
    assert 'value="option_003"' in html
    assert "Ubuntu" in html
    assert "RedHat" in html
    assert "Windows" in html


def test_free_comment_control_is_multiline_and_stable():
    field_name = free_comment_field_name("general-notes", "index")
    html = free_comment_control_html("Allgemeine Anmerkungen", field_name, rows=5)

    assert "Allgemeine Anmerkungen:" in html
    assert "<textarea" in html
    assert f'name="{field_name}"' in html
    assert 'rows="5"' in html
