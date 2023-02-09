from docutils.parsers.rst import Directive, directives, nodes
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.errors import ExtensionError
from sphinx.util import logging

logger = logging.getLogger(__name__)

import sys
import re

_module = sys.modules[__name__]
_module.cases = {}
_module.actions = {}
_module.case_id = 0
_module.action_id = 0

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
        "title": directives.unchanged,
#        "columns": directives.unchanged,
        "class": directives.unchanged,
#        "header-rows": int,
    }

    def handle_signature(self, sig, signode):
        logger.debug(f"handle_signature in test case directive {sig}")
        print(f"handle_signature in test case directive {sig}")


    def run(self):
        env = self.env
        classes = ["case"]

        if "class" in self.options:
            classes.append(self.options["class"])

        headers = []
        widths = []
        columns = None
        case_id = None
        caption = self.arguments[0]

        logger.debug(f"got caption {caption}")
        ids = [f"table-{caption}"]

        if "id" in self.options:
            case_id = self.options["id"]
            ids.append(f"test-case-{case_id}")

        node_table = nodes.table(classes=classes, ids=ids)

        if "title" in self.options:
            node_caption = nodes.title(text=caption)
            node_table += node_caption

        #if "headers" in self.options and 0 < len(self.options["headers"]):
        #    headers = re.split(",\s{0,1}", self.options["headers"] )
        #    logger.debug(f"found {len(headers)} entries in header")
        #    logger.warning(f"use of headers option is deprecated, use :header-rows: instead")
        #    columns = len(headers)

        #if "widths" in self.options and 0 < len(self.options["widths"]):
        #    widths = re.split(",\s{0,1}", self.options["widths"] )
        #    logger.debug(f"found {len(widths)} entries in widths")
        #    columns = len(widths)

        #if "columns" in self.options:
        #    columns = int(self.options["columns"])
        #    if env.config.rst_table_autonumber:
        #        columns += 1

        #elif "headers" not in self.options and "widths" not in self.options:
        #    raise ExtensionError(
        #        "could not determine number of columns from header or widths options. 'columns' options must be given"
        #    )

        #if "header-rows" in self.options:
        #    _module.header_rows = int(self.options["header-rows"])
        #    _module.header_rows = int(self.options["header-rows"])

        columns = 4 # id, action, reaction, success
        headers=["id","action","reaction","success"]

        logger.debug(f"create test case with {columns} columns")
        print(f"create test case with {columns} columns")

        #if env.config.rst_table_autonumber_reset_on_table:
        #    _module.case_id = 0        _module.row_id += 1


        _module.action_id = 0
        _module.case_id += 1

        node_tgroup = nodes.tgroup(cols=columns)
        node_table += node_tgroup

        # todo match headers and widths length to match together
        #if 0 < len(widths):
        #    for width in widths:
        #        logger.debug(f"create colspec with {int(width)} column")
        #        node_colspec = nodes.colspec(colwidth=int(width))
        #        node_tgroup += node_colspec
        #else:

        for i in range(0, columns):
            logger.debug(f"create colspec with {int(100/columns)} column")
            node_colspec = nodes.colspec(colwidth=int(100 / columns))
            node_tgroup += node_colspec

        if 0 < len(headers):
            header_row = nodes.row()
            for header in headers:
                header_row += nodes.entry("", nodes.paragraph(text=header))

            node_thead = nodes.thead("", header_row)
            node_tgroup += node_thead
            nodes_content = nodes.tbody()
        else:
            nodes_content = nodes.tbody();

        self.state.nested_parse(self.content, self.content_offset, nodes_content)

        node_tgroup += nodes_content

        if caption is not None or case_id is not None:
            test_domain = self.env.get_domain("test")
            test_domain.add_case(caption, case_id)
        return [node_table]


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
    #    "id": directives.unchanged,
    #    "class": directives.unchanged,
    }

    def handle_signature(self, sig, signode):
        print(f"handle_signature in action directive {sig}")


    def run(self):
        env = self.env
        classes =  ["test-action"]

        ids=[]
        kwargs = {}

        # todo add odd/even to clases
        if "class" in self.options:
            classes.append(self.options["classes"])

        _module.row_anchor = None


        if "id" in self.options:
            _module.row_anchor = f"test-action-{self.options['id']}"
            logger.debug(f"storing test action anchor test-action-{_module.row_anchor}")

        logger.debug(f"adding test action as row with content {self.content}")
        node_row = nodes.row(classes=['test-action-row'])

        kwargs['classes']=classes

        node_id = nodes.entry(**kwargs)
        node_id_text = nodes.Text(f"{_module.case_id}.{_module.action_id}")
        node_id += node_id_text

        _module.action_id += 1

        node_action = nodes.entry(classes=classes, ids=ids)

        #node_row += node_action
        #content_row += node_row

        self.state.nested_parse(self.content, self.content_offset, node_action)

        node_row += node_id
        node_row += node_action

        return [node_row]

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
        classes =  ["test-reaction"]

        # todo add odd/even to clases
        if "class" in self.options:
            classes.append(self.options["classes"])

        logger.debug(f"adding test reaction with content {self.content}")
        self.assert_has_content()
        ids = []

        kwargs['classes']=classes

        if _module.row_anchor is not None:
            ids.append(_module.row_anchor)
            _module.row_anchor = []
        #if "colspan" in self.options:
        #    morecols = int(self.options["colspan"]) - 1
        #    kwargs['morecols']=morecols
        #if "rowspan" in self.options:
        #    morerows = int(self.options["rowspan"]) - 1
        #    kwargs['morerows']=morerows
        return []

        node = nodes.entry(**kwargs)
        # node = nodes.entry(classes=classes, ids=ids )
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
