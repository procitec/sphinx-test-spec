import json

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


def test_build_result_preserves_optional_action_and_reaction_ids():
    manifest = {
        "document": {"id": "manual", "spec_hash": "sha256:test"},
        "namespace": "category.appname",
        "cases": [
            {
                "id": "startup",
                "title": "Startup",
                "steps": [
                    {
                        "number": 1,
                        "action": "Start",
                        "reaction": "Runs",
                        "result_field": "r1",
                        "action_id": "ACT_START",
                        "reaction_id": "REACT_RUNNING",
                    },
                    {
                        "number": 2,
                        "action": "Stop",
                        "reaction": "Stops",
                        "result_field": "r2",
                        "action_id": "ACT_STOP",
                    },
                    {
                        "number": 3,
                        "action": "Wait",
                        "reaction": "Ready",
                        "result_field": "r3",
                        "reaction_id": "REACT_READY",
                    },
                    {"number": 4, "action": "Check", "reaction": "OK", "result_field": "r4"},
                ],
            },
        ],
    }

    result = build_result(manifest, {"r1": "passed", "r2": "na", "r3": "passed", "r4": "passed"}, {}, "linux")
    assert result.cases[0].steps[0].action_id == "ACT_START"
    assert result.cases[0].steps[0].reaction_id == "REACT_RUNNING"
    assert result.cases[0].steps[1].reaction_id is None
    assert result.cases[0].steps[2].action_id is None

    # JSON serialization matches the output of testspec-result --result-json.
    serialized = json.loads(json.dumps(result.to_dict()))
    steps = serialized["cases"][0]["steps"]
    assert steps[0]["action_id"] == "ACT_START"
    assert steps[0]["reaction_id"] == "REACT_RUNNING"
    assert steps[0]["result"] == "passed"
    assert steps[1]["action_id"] == "ACT_STOP"
    assert "reaction_id" not in steps[1]
    assert "action_id" not in steps[2]
    assert steps[2]["reaction_id"] == "REACT_READY"
    assert "action_id" not in steps[3]
    assert "reaction_id" not in steps[3]
    assert serialized["cases"][0]["qualified_id"] == "linux.category.appname.startup"
