from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

STEP_RESULTS = {"passed", "failed", "na"}
CASE_RESULTS = {"passed", "failure", "error", "skipped"}


class ResultProcessingError(ValueError):
    """Raised when a manual test result cannot be processed safely."""


@dataclass(frozen=True)
class StepResult:
    number: int
    action: str
    reaction: str
    result_field: str
    result: str | None


@dataclass(frozen=True)
class CaseResult:
    id: str
    qualified_id: str
    title: str
    status: str
    status_reason: str
    comment: str
    steps: tuple[StepResult, ...]


@dataclass(frozen=True)
class TestSpecResult:
    document: dict[str, Any]
    namespace: str
    execution_prefix: str
    cases: tuple[CaseResult, ...]

    def counts(self) -> dict[str, int]:
        counts = Counter(case.status for case in self.cases)
        return {status: counts.get(status, 0) for status in ("passed", "failure", "error", "skipped")}

    def to_dict(self) -> dict[str, Any]:
        counts = self.counts()
        return {
            "schema_version": 1,
            "document": self.document,
            "namespace": self.namespace,
            "execution_prefix": self.execution_prefix,
            "summary": {
                "tests": len(self.cases),
                "passed": counts["passed"],
                "failures": counts["failure"],
                "errors": counts["error"],
                "skipped": counts["skipped"],
            },
            "cases": [asdict(case) for case in self.cases],
        }


def join_test_id(*parts: str) -> str:
    cleaned = [part.strip(".") for part in parts if part and part.strip(".")]
    return ".".join(cleaned)


def aggregate_status(results: list[str | None]) -> tuple[str, str]:
    if not results or all(result is None for result in results):
        return "skipped", "not-executed"

    invalid = {result for result in results if result is not None and result not in STEP_RESULTS}
    if invalid:
        values = ", ".join(sorted(invalid))
        raise ResultProcessingError(f"unknown step result value(s): {values}")

    if "failed" in results:
        return "failure", "failed-step"

    if any(result is None for result in results):
        return "error", "incomplete"

    if all(result == "na" for result in results):
        return "skipped", "not-applicable"

    if all(result in {"passed", "na"} for result in results) and "passed" in results:
        return "passed", "completed"

    raise ResultProcessingError(f"cannot aggregate step results: {results!r}")


def build_result(
    manifest: dict[str, Any],
    field_values: Mapping[str, str | None],
    comments: Mapping[str, str],
    execution_prefix: str,
) -> TestSpecResult:
    namespace = str(manifest.get("namespace", "")).strip(".")
    prefix = execution_prefix.strip(".")
    case_results: list[CaseResult] = []

    for index, case in enumerate(manifest.get("cases", []), start=1):
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            title = case.get("title") or f"case {index}"
            raise ResultProcessingError(f"test case {title!r} has no stable :id: and cannot be exported to JUnit")

        step_results: list[StepResult] = []
        for step in case.get("steps", []):
            field_name = step.get("result_field")
            if not isinstance(field_name, str) or not field_name:
                raise ResultProcessingError(
                    f"test case {case_id!r}, step {step.get('number')!r} has no result_field in the manifest"
                )
            result = field_values.get(field_name)
            step_results.append(
                StepResult(
                    number=int(step.get("number", len(step_results) + 1)),
                    action=str(step.get("action", "")),
                    reaction=str(step.get("reaction", "")),
                    result_field=field_name,
                    result=result,
                )
            )

        status, reason = aggregate_status([step.result for step in step_results])
        comment_field = case.get("comment_field")
        comment = comments.get(comment_field, "") if isinstance(comment_field, str) else ""
        case_results.append(
            CaseResult(
                id=case_id,
                qualified_id=join_test_id(prefix, namespace, case_id),
                title=str(case.get("title", case_id)),
                status=status,
                status_reason=reason,
                comment=comment,
                steps=tuple(step_results),
            )
        )

    return TestSpecResult(
        document=dict(manifest.get("document", {})),
        namespace=namespace,
        execution_prefix=prefix,
        cases=tuple(case_results),
    )
