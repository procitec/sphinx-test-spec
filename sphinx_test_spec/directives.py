from docutils.parsers.rst import Directive, directives, nodes
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.errors import ExtensionError
from sphinx.util import logging

#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

import sys
import re

_module = sys.modules[__name__]
_module.cases = {}
_module.actions = {}
_module.case_id = 0
_module.action_id = 0
_module.node_reaction = None
_module.node_table = None
_module.node_table_id = None
_module.node_thead = None
_module.node_tgroup = None
_module.node_tbody = None
_module.node_thead = None
_module.node_colspec = None
_module.columns = 4
_module.headers = ["id","action","reaction","ok"]

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

    def handle_signature(self, sig, signode):
        logger.debug(f"handle_signature in test case directive {sig}")
        print(f"handle_signature in test case directive {sig}")


    def run(self):
        env = self.env
        classes = ["test-case"]
        _class_test_case_section = "test-case-section"
        _class_test_case_content = "test-case-content"


        if "class" in self.options:
            classes.append(self.options["class"])

        widths = []
        case_id = None
        caption = self.arguments[0]

        logger.info(f"got caption {caption}")
        ids = [f"test-case-{caption}"]

        required_arguments = 1
        final_argument_whitespace = True

        node_section = nodes.section(ids=ids, classes=[_class_test_case_section])
        node_section += nodes.title(text=caption)

        #if "id" in self.options:
        #    case_id = self.options["id"]
        #    ids.append(f"test-case-{case_id}")
        #if "widths" in self.options and 0 < len(self.options["widths"]):
        #    widths = re.split(",\s{0,1}", self.options["widths"] )
        #    logger.debug(f"found {len(widths)} entries in widths")
        #    columns = len(widths)

        logger.debug(f"create test case with {_module.columns} columns")
        #print(f"create test case with {_module.columns} columns")

        if 0 < len(env.config.testspec_header):
            if 4 == len(env.config.testspec_header):
                _module.headers = env.config.testspec_header
            else:
                logger.error(f"lenght of config heaaders {len(env.config.testspec_header)} does not match required header length 4")

        if not len(_module.headers) == _module.columns:
            logger.error(f"configured headers length {len(_module.headers)} does not match required length {_module.columns}")

        _module.action_id = 0
        _module.case_id += 1

        _module.node_table = None
        _module.node_thead = None
        _module.node_tgroup = None
        _module.node_tbody = None
        _module.node_thead = None
        _module.node_colspec = None
        _module.node_table_id = [f"test-case-table-{caption}"]

        _module.node_table = nodes.table(classes=["test-case-table"], ids=_module.node_table_id)

        _module.node_tgroup = nodes.tgroup(cols=_module.columns)
        _module.node_table += _module.node_tgroup

        for i in range(0, _module.columns):
            logger.debug(f"create colspec with {int(100/_module.columns)} column")
            _module.node_colspec = nodes.colspec(colwidth=int(100 / _module.columns))
            _module.node_tgroup += _module.node_colspec

        if 0 < len(_module.headers):
            header_row = nodes.row()
            for header in _module.headers:
                header_row += nodes.entry("", nodes.paragraph(text=header))

            _module.node_thead = nodes.thead("", header_row, classes=['test-case-table-head'])
            _module.node_tgroup += _module.node_thead
            _module.node_tbody = nodes.tbody()

        node_case = nodes.container(classes=[_class_test_case_content])

        self.state.nested_parse(self.content, self.content_offset, node_case)

        _module.node_tgroup += _module.node_tbody

        node_section += node_case
        node_section += _module.node_table

        if caption is not None or case_id is not None: #this should never occur
            test_domain = self.env.get_domain("test")
            test_domain.add_case(caption, case_id)

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
    #    "id": directives.unchanged,
    #    "class": directives.unchanged,
    }

    def handle_signature(self, sig, signode):
        print(f"handle_signature in action directive {sig}")


    def run(self):
        env = self.env
        classes =  ["test-action"]
        _class_test_action = "test-action"
        _class_test_action_row = _class_test_action + "-row"
        _class_test_action_id = _class_test_action + "-id"
        _class_test_action_state = _class_test_action + "-state"


        ids=[]
        kwargs = {}

        # todo add odd/even to clases
        if "class" in self.options:
            classes.append(self.options["classes"])

        #_module.row_anchor = None
        #if "id" in self.options:
        #    _module.row_anchor = f"test-action-{self.options['id']}"
        #    logger.debug(f"storing test action anchor test-action-{_module.row_anchor}")

        logger.debug(f"adding test action as row with content {self.content}")
        node_row = nodes.row(classes=[_class_test_action_row])

        kwargs['classes']=classes

        node_id = nodes.entry(classes=[_class_test_action_id])
        node_id_text = nodes.Text(f"{_module.case_id}.{_module.action_id}")
        node_id += node_id_text

        _module.action_id += 1

        node_action = nodes.entry(classes=classes, ids=ids)
        _module.node_reaction = None

        self.state.nested_parse(self.content, self.content_offset, node_action)

        node_row += node_id
        node_row += node_action
        if _module.node_reaction is not None:
            node_row += _module.node_reaction
        else:
            node_row += nodes.entry()

        state_symbol= env.config.testspec_state_symbol

        node_state = nodes.entry(classes=[_class_test_action_state])
        node_state_text = nodes.Text(state_symbol)
        node_state += node_state_text

        node_row += node_state
        _module.node_tbody += node_row

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
        classes =  ["test-reaction"]

        # todo add odd/even to clases
        if "class" in self.options:
            classes.append(self.options["classes"])

        logger.debug(f"adding test reaction with content {self.content}")
        self.assert_has_content()
        ids = []

        kwargs['classes']=classes

        # the reaction directive could occur only onces or never in an action
        if _module.node_reaction is None:

            node = nodes.entry(**kwargs)
            # node = nodes.entry(classes=classes, ids=ids )
            self.state.nested_parse(self.content, self.content_offset, node)

            _module.node_reaction = node
        else:
            logger.error("reaction diretive already defined in a test::action, could occur only once!")

        return []
