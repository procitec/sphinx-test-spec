from pathlib import Path

import pytest
from sphinx.util import logging

logger = logging.getLogger(__name__)

import json
import sys


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "testspec", "srcdir": "doc_test/doc_builder_file_json", "warnings": sys.stderr}],
    indirect=True,
)
def test_doc_builder_file_json(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html")
    assert not html.exists()
    json_content = json.loads(Path(app.outdir, "testspec.json").read_text())

    warning = app._warning
    warnings = warning.getvalue()

    assert 3 == len(json_content["files"].keys())
    assert "index" == json_content["document"]
    assert sorted(json_content["files"].keys()) == ["/a/b/c/filein/test2.snd", "signal.wav", "signals/test1.wav"]
    for f in json_content["files"].keys():
        assert "suffix" in json_content["files"][f]
        assert "path" in json_content["files"][f]
        assert "name" in json_content["files"][f]
