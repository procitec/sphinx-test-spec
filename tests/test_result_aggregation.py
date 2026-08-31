import pytest

from sphinx_test_spec.result import ResultProcessingError, aggregate_status, build_result


def test_aggregate_status():
    assert aggregate_status([None, None]) == ("skipped", "not-executed")
    assert aggregate_status(["passed", "failed", None]) == ("failure", "failed-step")
    assert aggregate_status(["passed", None]) == ("error", "incomplete")
    assert aggregate_status(["na", "na"]) == ("skipped", "not-applicable")
    assert aggregate_status(["passed", "na"]) == ("passed", "completed")


def test_build_result_adds_execution_prefix():
    manifest = {
        "document": {"id": "manual", "spec_hash": "sha256:test"},
        "namespace": "category.appname",
        "cases": [
            {
                "id": "startup",
                "title": "Startup",
                "comment_field": "comment",
                "steps": [
                    {"number": 1, "action": "Start", "reaction": "Runs", "result_field": "result_1"},
                    {"number": 2, "action": "Stop", "reaction": "Stops", "result_field": "result_2"},
                ],
            }
        ],
    }

    result = build_result(
        manifest,
        {"result_1": "passed", "result_2": "na"},
        {"comment": "Executed on target"},
        "linux.x86_64",
    )

    case = result.cases[0]
    assert case.qualified_id == "linux.x86_64.category.appname.startup"
    assert case.status == "passed"
    assert case.comment == "Executed on target"


def test_build_result_requires_stable_case_id():
    manifest = {
        "document": {},
        "namespace": "category",
        "cases": [{"id": None, "title": "No id", "steps": []}],
    }

    with pytest.raises(ResultProcessingError, match="no stable :id:"):
        build_result(manifest, {}, {}, "linux")
