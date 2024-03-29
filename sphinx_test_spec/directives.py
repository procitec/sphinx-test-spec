from docutils.parsers.rst import Directive, directives, nodes
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.errors import ExtensionError
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

# logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

import re
import sys


class TestCaseDirective(ObjectDescription):
    """A custom directive that describes a test case in the test domain.

    The created table must have the following docutils structure::

        - table
        -- tgroup
        --- colspec (partial used)
        --- thead (not used)
        --- tbody
        ---- row
        ----- entry
        ------ custom layout nodes
    """

    has_content = True
    required_arguments = 1
    option_spec = {
        #        "headers": directives.unchanged,
        #        "widths": directives.unchanged,
        #        "title": directives.unchanged,
        #        "columns": directives.unchanged,
        "class": directives.unchanged,
        #        "header-rows": int,
    }

    def run(self):
        env = self.env
        classes = ["test-case"]
        _class_test_case_section = "test-case-section"
        _class_test_case_content = "test-case-content"

        if "class" in self.options:
            classes.append(self.options["class"])

        widths = []
        # case_id = None
        caption = self.arguments[0]
        test_domain = self.env.get_domain("test")
        _state = test_domain.data["state"]

        self.state.inline_text(caption, 0)

        textnodes, messages = self.state.inline_text(caption, self.lineno)

        logger.info(f"got caption {caption} {textnodes}")
        ids = [f"test-case-{caption}"]

        required_arguments = 1
        final_argument_whitespace = True

        node_section = nodes.section(ids=ids, classes=[_class_test_case_section])
        node_section += nodes.title(caption, "", *textnodes)

        # if "id" in self.options:
        #    case_id = self.options["id"]
        #    ids.append(f"test-case-{case_id}")
        # if "widths" in self.options and 0 < len(self.options["widths"]):
        #    widths = re.split(",\s{0,1}", self.options["widths"] )
        #    logger.debug(f"found {len(widths)} entries in widths")
        #    columns = len(widths)

        logger.debug(f"create test case with {_state.columns} columns")

        if 0 < len(env.config.testspec_header):
            if 4 == len(env.config.testspec_header):
                _state.headers = env.config.testspec_header
            else:
                logger.error(
                    f"lenght of config heaaders {len(env.config.testspec_header)} does not match required header length 4"
                )

        if 0 < len(env.config.testspec_header_widths):
            if 4 == len(env.config.testspec_header_widths):
                widths = env.config.testspec_header_widths
            else:
                logger.error(
                    f"lenght of config heaaders widths {len(env.config.testspec_header_widths)} does not match required header length 4"
                )

        if not len(_state.headers) == _state.columns:
            logger.error(
                f"configured headers length {len(_state.headers)} does not match required length {_state.columns}"
            )

        _state.action_id = 0
        _state.case_id += 1

        _state.node_table = None
        _state.node_thead = None
        _state.node_tgroup = None
        _state.node_tbody = None
        _state.node_thead = None
        # _state.node_table_id = [f"test-case-{caption}"] #no extra reference of table as role, just the section from the case

        # class "colwidths-given" must be set since docutils-0.18.1, otherwise the table will not have
        # any colgroup definitions.
        class_colwidth = "colwidths-given" if 0 < len(widths) else "colwidths-auto"

        _state.node_table = nodes.table(classes=classes + [class_colwidth])  # , ids=_state.node_table_id)

        _state.node_tgroup = nodes.tgroup(cols=_state.columns)

        for i in range(0, _state.columns):
            if 0 < len(widths):
                node_colspec = nodes.colspec(colwidth=widths[i])
            else:
                node_colspec = nodes.colspec()

            _state.node_tgroup += node_colspec

        header_row = nodes.row()

        if 0 < len(_state.headers):
            for header in _state.headers:
                node_th = nodes.entry("", nodes.Text(header))
                header_row += node_th

        _state.node_thead = nodes.thead("", header_row, classes=["test-case-head"])

        _state.node_tgroup += _state.node_thead
        _state.node_tbody = nodes.tbody()

        node_case = nodes.container(classes=[_class_test_case_content])

        self.state.nested_parse(self.content, self.content_offset, node_case)

        _state.node_tgroup += _state.node_tbody
        _state.node_table += _state.node_tgroup

        node_section += node_case
        node_section += _state.node_table

        assert caption is not None

        # if caption is not None# or case_id is not None: #this should never occur
        test_domain.add_case(caption)  # , case_id)

        return [node_section]


class ActionDirective(ObjectDescription):
    """A custom directive that describes a row in a table in the test domain.

    Builds a need based on a given layout for a given need-node.

    The created table must have the following docutils structure::

        - table
        -- tgroup
        --- colspec (partial used)
        --- thead (not used)
        --- tbody
        ---- row
        ----- entry
        ------ custom layout nodes
    """

    has_content = True
    required_arguments = 0
    option_spec = {
        "id": directives.unchanged,
        "class": directives.unchanged,
    }

    def run(self):
        env = self.env
        classes = ["test-action"]
        _class_test_action = "test-action"
        _class_test_action_row = _class_test_action
        _class_test_action_id = _class_test_action + "-id"
        _class_test_action_state = _class_test_action + "-state"

        ids = []
        kwargs = {}
        action_anchor = None
        test_domain = self.env.get_domain("test")

        _state = test_domain.data["state"]

        # todo add odd/even to clases
        if "class" in self.options:
            classes.append(self.options["class"])

        node_row = nodes.row(classes=[_class_test_action_row])

        if "id" in self.options:
            action_anchor = f"test-action-{_state.case_id}.{self.options['id']}"
            # action_anchor = f"test-action-{self.options['id']}"
            ids.append(action_anchor)
            logger.debug(f"storing test action anchor test-action-{action_anchor}")

        logger.debug(f"adding test action as row with content {self.content}")

        kwargs["classes"] = classes

        action_id_text = f"{_state.case_id}.{_state.action_id}"

        node_id = nodes.entry(classes=[_class_test_action_id], ids=ids)
        node_id_text = nodes.Text(action_id_text)
        node_id += node_id_text

        _state.action_id += 1

        node_action = nodes.entry(classes=classes)  # , ids=ids)
        _state.node_reaction = None

        self.state.nested_parse(self.content, self.content_offset, node_action)

        node_row += node_id
        node_row += node_action
        if _state.node_reaction is not None:
            node_row += _state.node_reaction
        else:
            node_row += nodes.entry()

        state_symbol = env.config.testspec_state_symbol

        node_state = nodes.entry(classes=[_class_test_action_state])
        node_state_text = nodes.Text(state_symbol)
        node_state += node_state_text

        node_row += node_state
        _state.node_tbody += node_row

        if "id" in self.options:
            test_domain.add_action(_state.case_id, self.options["id"], action_id_text)

        return []


class ReactionDirective(ObjectDescription):
    """A custom directive that describes a column in a table in the tbl domain."""

    has_content = True
    required_arguments = 0
    option_spec = {
        "class": directives.unchanged,
        #        "colspan": int,
        #        "rowspan": int,
    }

    def run(self):
        kwargs = {}
        classes = ["test-reaction"]

        # todo add odd/even to clases
        if "class" in self.options:
            classes.append(self.options["class"])

        logger.debug(f"adding test reaction with content {self.content}")
        self.assert_has_content()
        ids = []
        test_domain = self.env.get_domain("test")

        _state = test_domain.data["state"]

        kwargs["classes"] = classes

        # the reaction directive could occur only onces or never in an action
        if _state.node_reaction is None:
            node = nodes.entry(**kwargs)
            # node = nodes.entry(classes=classes, ids=ids )
            self.state.nested_parse(self.content, self.content_offset, node)

            _state.node_reaction = node
        else:
            logger.error("reaction diretive already defined in a test::action, could occur only once!")

        return []


class FileListDirective(SphinxDirective):
    has_content = False
    required_arguments = 0
    option_spec = {
        "filter": directives.unchanged,
        "class": directives.unchanged,
    }

    def run(self):
        logger.debug(f"adding test filelist")
        test_domain = self.env.get_domain("test")
        _files = test_domain.data["files"]
        _content = []
        _classes = ["test-filelist"]

        if "filter" in self.options:
            filter_string = self.options["filter"]

            for k, v in _files.items():
                name = v["name"]
                suffix = v["suffix"]
                if bool(eval(filter_string, None, locals())):
                    _content.append(k)
        else:
            for k, v in _files.items():
                _content.append(k)

        if "class" in self.options:
            _classes.append(self.options["class"])

        listnode = nodes.bullet_list(classes=_classes)
        for entry in _content:
            listnode += nodes.list_item("", nodes.Text(entry), classes=["test-filelist-item"])

        return [listnode]
