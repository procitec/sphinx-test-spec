from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from sphinx_test_spec.junit import write_junit
from sphinx_test_spec.result import ResultProcessingError
from sphinx_test_spec.result_pdf import DEFAULT_MANIFEST_NAME, read_pdf_result

PACKAGE_NAME = "sphinx-test-spec"


def _version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0+unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="testspec-result",
        description="Extract a filled sphinx-test-spec PDF form and write JUnit/result JSON.",
    )
    parser.add_argument("pdf", help="filled PDF test specification")
    parser.add_argument(
        "--execution-prefix",
        default="",
        help="prefix added before the build-time namespace, e.g. linux or windows.x86_64",
    )
    parser.add_argument("--junit", help="write JUnit XML to this path")
    parser.add_argument("--result-json", help="optionally write the normalized result model as JSON")
    parser.add_argument("--manifest", help="use/verify an external testspec-manifest.json")
    parser.add_argument(
        "--manifest-name",
        default=DEFAULT_MANIFEST_NAME,
        help=f"embedded manifest attachment name (default: {DEFAULT_MANIFEST_NAME})",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_version()}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.junit and not args.result_json:
        parser.error("at least one output is required: --junit and/or --result-json")

    try:
        result = read_pdf_result(
            args.pdf,
            execution_prefix=args.execution_prefix,
            external_manifest=args.manifest,
            manifest_name=args.manifest_name,
        )
        if args.junit:
            write_junit(result, args.junit)
        if args.result_json:
            target = Path(args.result_json)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    except ResultProcessingError as exc:
        print(f"testspec-result: error: {exc}", file=sys.stderr)
        return 2

    counts = result.counts()
    print(
        "Processed "
        f"{len(result.cases)} test case(s): "
        f"{counts['passed']} passed, {counts['failure']} failed, "
        f"{counts['error']} incomplete, {counts['skipped']} skipped."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
