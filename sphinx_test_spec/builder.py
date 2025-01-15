from __future__ import annotations

import json
import os
from collections.abc import Iterable, Sequence

from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.util import logging

from sphinx_test_spec.domain import TestSpecDomain

LOGGER = logging.getLogger(__name__)


class TestSpecBuilder(Builder):
    """Output the testspec data as a JSON file,

    Note this builder normally completely skips the write phase,
    where all documents are post-transformed, to improve performance.
    It is assumed all need data is already read in the read phase,
    and the post-processing of the data is done in the finish phase.
    """

    name = "testspec"
    format = "json"
    file_suffix = ".json"
    links_suffix = None

    def get_outdated_docs(self) -> Iterable[str]:
        return []

    def write(
        self,
        build_docnames: Iterable[str] | None,
        updated_docnames: Sequence[str],
        method: str = "update",
    ) -> None:
        return

    def finish(self) -> None:
        test_domain = self.env.get_domain("test")
        content = {"project": self.app.config.project, "document": self.app.config.master_doc}
        _out = os.path.join(self.outdir, "testspec.json")

        if "files" in test_domain.data:
            files = test_domain.data["files"]
            if 0 < len(files):
                content["files"] = files

        with open(_out, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4, sort_keys=True)

    def get_target_uri(self, _docname: str, _typ: str | None = None) -> str:
        # only needed if the write phase is run
        return ""

    def prepare_writing(self, _docnames: set[str]) -> None:
        # only needed if the write phase is run
        pass

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        # only needed if the write phase is run
        pass

    def write_doc_serialized(self, _docname: str, _doctree: nodes.document) -> None:
        # only needed if the write phase is run
        pass

    def cleanup(self) -> None:
        # only needed if the write phase is run
        pass


def build_testspec_json(app: Sphinx, _exception: Exception) -> None:
    env = app.env

    # Do not create an additional testspec.json, if builder is already "testspec".
    if isinstance(app.builder, TestSpecBuilder):
        return

    _builder = TestSpecBuilder(app, env)
    _builder.finish()
