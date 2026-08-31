from __future__ import annotations

from collections.abc import Iterable, Sequence

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders import Builder

from sphinx_test_spec.artifacts import write_testspec_manifest, write_testspec_resources


class TestSpecBuilder(Builder):
    """Output test specification artifacts as JSON files.

    The builder skips the normal write phase. Referenced resources and the
    execution manifest are generated from data collected by the test domain
    during the read phase.
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
        write_testspec_resources(self.app, self.outdir)
        write_testspec_manifest(self.app, self.outdir)

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


def build_testspec_artifacts(app: Sphinx, exception: Exception | None) -> None:
    if exception is not None:
        return

    # The testspec builder already writes both artifacts in finish().
    if isinstance(app.builder, TestSpecBuilder):
        return

    write_testspec_resources(app, app.outdir)
    write_testspec_manifest(app, app.outdir)


# Backwards-compatible function name for users importing the old helper.
def build_testspec_json(app: Sphinx, exception: Exception | None) -> None:
    build_testspec_artifacts(app, exception)
