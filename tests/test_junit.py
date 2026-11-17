from io import BytesIO

from sphinx_test_spec.junit import build_junit_tree
from sphinx_test_spec.result import build_result


def test_junit_contains_aggregated_cases():
    manifest = {
        "document": {"id": "manual", "spec_hash": "sha256:test"},
        "namespace": "category.appname",
        "cases": [
            {
                "id": "startup",
                "title": "Startup",
                "comment_field": "comment",
                "steps": [
                    {"number": 1, "action": "Start", "reaction": "Runs", "result_field": "r1"},
                    {"number": 2, "action": "Check", "reaction": "Ready", "result_field": "r2"},
                ],
            },
            {
                "id": "shutdown",
                "title": "Shutdown",
                "comment_field": "comment2",
                "steps": [
                    {"number": 1, "action": "Stop", "reaction": "Stops", "result_field": "r3"},
                ],
            },
        ],
    }
    result = build_result(
        manifest,
        {"r1": "passed", "r2": "failed", "r3": None},
        {"comment": "Unexpected dialog"},
        "linux",
    )

    tree = build_junit_tree(result)
    output = BytesIO()
    tree.write(output, encoding="utf-8", xml_declaration=True)
    xml = output.getvalue().decode("utf-8")

    assert 'tests="2"' in xml
    assert 'failures="1"' in xml
    assert 'skipped="1"' in xml
    assert 'name="linux.category.appname.startup"' in xml
    assert 'classname="linux.category.appname"' in xml
    assert "Unexpected dialog" in xml
    assert "Manual test case not executed" in xml
