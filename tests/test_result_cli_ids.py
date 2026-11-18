import json
from xml.etree import ElementTree as ET

from pypdf import PdfWriter

from sphinx_test_spec.manifest import with_spec_hash
from sphinx_test_spec.result_cli import main


def test_result_cli_exports_optional_step_ids_from_embedded_manifest(tmp_path):
    manifest = with_spec_hash(
        {
            "schema_version": 1,
            "document": {"id": "manual", "title": "Manual", "source": "index"},
            "namespace": "category.appname",
            "cases": [
                {
                    "docname": "index",
                    "id": "startup",
                    "title": "Startup",
                    "steps": [
                        {
                            "number": 1,
                            "action": "Start CamelBrand.",
                            "reaction": "CamelBrand is ready.",
                            "action_id": "ACT_START",
                            "reaction_id": "REACT_READY",
                            "result_field": "r1",
                        },
                        {
                            "number": 2,
                            "action": "Stop",
                            "reaction": "Stopped",
                            "result_field": "r2",
                        },
                    ],
                }
            ],
        }
    )
    pdf = tmp_path / "filled.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_attachment("testspec-manifest.json", json.dumps(manifest).encode("utf-8"))
    with pdf.open("wb") as stream:
        writer.write(stream)

    result_json = tmp_path / "result.json"
    junit_xml = tmp_path / "result.xml"
    assert (
        main([str(pdf), "--execution-prefix", "linux", "--result-json", str(result_json), "--junit", str(junit_xml)])
        == 0
    )

    result = json.loads(result_json.read_text(encoding="utf-8"))
    case = result["cases"][0]
    assert case["qualified_id"] == "linux.category.appname.startup"
    assert case["status"] == "skipped"  # Blank PDF has no selected form fields.
    assert case["steps"][0]["action_id"] == "ACT_START"
    assert case["steps"][0]["reaction_id"] == "REACT_READY"
    assert case["steps"][0]["action"] == "Start CamelBrand."
    assert "action_id" not in case["steps"][1]
    assert "reaction_id" not in case["steps"][1]

    junit = ET.parse(junit_xml)
    testcase = junit.find("./testsuite/testcase")
    assert testcase is not None
    assert testcase.get("name") == "startup"
    assert testcase.get("classname") == "linux.category.appname"
    assert testcase.find("skipped") is not None
