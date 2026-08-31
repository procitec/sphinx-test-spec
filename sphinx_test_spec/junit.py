from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from sphinx_test_spec.result import CaseResult, TestSpecResult, join_test_id


def _step_label(case: CaseResult, number: int) -> str:
    for step in case.steps:
        if step.number == number:
            expected = step.reaction or step.action
            return f"Step {number}: {expected}" if expected else f"Step {number}"
    return f"Step {number}"


def _failure_text(case: CaseResult) -> str:
    lines = [f"{_step_label(case, step.number)} -> FAIL" for step in case.steps if step.result == "failed"]
    if case.comment:
        lines.extend(("", f"Comment: {case.comment}"))
    return "\n".join(lines)


def _error_text(case: CaseResult) -> str:
    lines = [f"{_step_label(case, step.number)} -> no result" for step in case.steps if step.result is None]
    if case.comment:
        lines.extend(("", f"Comment: {case.comment}"))
    return "\n".join(lines)


def _add_properties(parent: ET.Element, result: TestSpecResult, case: CaseResult) -> None:
    properties = ET.SubElement(parent, "properties")
    values = {
        "testspec.id": case.id,
        "testspec.namespace": result.namespace,
        "testspec.execution_prefix": result.execution_prefix,
        "testspec.spec_hash": str(result.document.get("spec_hash", "")),
    }
    for name, value in values.items():
        ET.SubElement(properties, "property", name=name, value=value)


def build_junit_tree(result: TestSpecResult) -> ET.ElementTree:
    counts = result.counts()
    suite_name = str(result.document.get("id") or result.document.get("title") or "manual-tests")
    classname = join_test_id(result.execution_prefix, result.namespace)

    root = ET.Element(
        "testsuites",
        tests=str(len(result.cases)),
        failures=str(counts["failure"]),
        errors=str(counts["error"]),
        skipped=str(counts["skipped"]),
    )
    suite = ET.SubElement(
        root,
        "testsuite",
        name=suite_name,
        tests=str(len(result.cases)),
        failures=str(counts["failure"]),
        errors=str(counts["error"]),
        skipped=str(counts["skipped"]),
    )

    for case in result.cases:
        testcase = ET.SubElement(
            suite,
            "testcase",
            classname=classname,
            name=case.qualified_id,
        )
        _add_properties(testcase, result, case)

        if case.status == "failure":
            failure = ET.SubElement(testcase, "failure", message="Manual test failed", type="failure")
            failure.text = _failure_text(case)
        elif case.status == "error":
            error = ET.SubElement(testcase, "error", message="Manual test case incomplete", type="incomplete")
            error.text = _error_text(case)
        elif case.status == "skipped":
            message = (
                "Manual test case not applicable"
                if case.status_reason == "not-applicable"
                else "Manual test case not executed"
            )
            ET.SubElement(testcase, "skipped", message=message)

        if case.comment and case.status in {"passed", "skipped"}:
            system_out = ET.SubElement(testcase, "system-out")
            system_out.text = f"Comment: {case.comment}"

    ET.indent(root, space="  ")
    return ET.ElementTree(root)


def write_junit(result: TestSpecResult, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    build_junit_tree(result).write(target, encoding="utf-8", xml_declaration=True)
