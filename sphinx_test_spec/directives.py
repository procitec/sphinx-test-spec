from docutils.parsers.rst import directives, nodes
from sphinx.directives import ObjectDescription
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from sphinx_test_spec.forms import (
    case_field_key,
    comment_control_html,
    comment_field_name,
    free_comment_control_html,
    free_comment_field_name,
    free_radio_control_html,
    free_radio_field_name,
    result_controls_html,
    result_field_name,
    result_header_html,
)

# logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


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
        "id": directives.unchanged,
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
        caption = self.arguments[0]
        case_id = self.options.get("id")
        test_domain = self.env.get_domain("test")
        _state = test_domain.data["state"]

        self.state.inline_text(caption, 0)

        textnodes, messages = self.state.inline_text(caption, self.lineno)

        logger.info(f"got caption {caption} {textnodes}")
        ids = [f"test-case-{caption}"]
        if case_id:
            ids.append(f"test-case-{case_id}")

        node_section = nodes.section(ids=ids, classes=[_class_test_case_section])
        node_title = nodes.title(caption, "", *textnodes)
        node_section += node_title

        # if "id" in self.options:
        #    case_id = self.options["id"]
        #    ids.append(f"test-case-{case_id}")
        # if "widths" in self.options and 0 < len(self.options["widths"]):
        #    widths = re.split(",\s{0,1}", self.options["widths"] )
        #    logger.debug(f"found {len(widths)} entries in widths")
        #    columns = len(widths)

        logger.debug(f"create test case with {_state.columns} columns")

        headers = list(_state.headers)
        if 0 < len(env.config.testspec_header):
            if 4 == len(env.config.testspec_header):
                headers = list(env.config.testspec_header)
            else:
                logger.error(
                    f"lenght of config heaaders {len(env.config.testspec_header)} "
                    "does not match required header length 4"
                )
        elif env.config.testspec_result_mode == "form":
            headers[-1] = ""

        if 0 < len(env.config.testspec_header_widths):
            if 4 == len(env.config.testspec_header_widths):
                widths = env.config.testspec_header_widths
            else:
                logger.error(
                    f"lenght of config heaaders widths {len(env.config.testspec_header_widths)} "
                    "does not match required header length 4"
                )

        if not len(headers) == _state.columns:
            logger.error(f"configured headers length {len(headers)} does not match required length {_state.columns}")

        _state.action_id = 0
        _state.case_id += 1
        case_number = _state.case_id
        field_key = case_field_key(case_id, env.docname, case_number)
        case_record = {
            "docname": env.docname,
            "id": case_id,
            "title": node_title.astext(),
            "comment_field": comment_field_name(field_key) if env.config.testspec_result_mode == "form" else None,
            "field_key": field_key if env.config.testspec_result_mode == "form" else None,
            "steps": [],
        }
        test_domain.data["manifest_cases"].append(case_record)
        _state.current_case = case_record

        if env.config.testspec_result_mode == "form" and not case_id:
            logger.warning(
                f"test:case '{node_title.astext()}' has no :id:; "
                "the result cannot be mapped to a stable external test id"
            )

        _state.node_table = None
        _state.node_thead = None
        _state.node_tgroup = None
        _state.node_tbody = None
        _state.node_thead = None

        # class "colwidths-given" must be set since docutils-0.18.1,
        # otherwise the table will not have any colgroup definitions.
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

        if 0 < len(headers):
            for index, header in enumerate(headers):
                if env.config.testspec_result_mode == "form" and index == _state.columns - 1:
                    node_th = nodes.entry()
                    node_th += nodes.raw(
                        "",
                        result_header_html(env.config.testspec_result_labels, header),
                        format="html",
                    )
                else:
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

        if env.config.testspec_result_mode == "form":
            node_section += nodes.raw(
                "",
                comment_control_html(case_record["comment_field"], env.config.testspec_comment_label),
                format="html",
            )

        assert caption is not None

        test_domain.add_case(caption, case_id)
        _state.current_case = None

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
        step_number = _state.action_id + 1

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

        node_state = nodes.entry(classes=[_class_test_action_state])
        if env.config.testspec_result_mode == "form":
            field_name = result_field_name(_state.current_case["field_key"], step_number)
            node_state += nodes.raw(
                "",
                result_controls_html(field_name, env.config.testspec_result_labels),
                format="html",
            )
        else:
            field_name = None
            node_state += nodes.Text(env.config.testspec_state_symbol)

        node_row += node_state
        _state.node_tbody += node_row

        if _state.current_case is not None:
            _state.current_case["steps"].append(
                {
                    "number": step_number,
                    "action": node_action.astext(),
                    "reaction": _state.node_reaction.astext() if _state.node_reaction is not None else "",
                    "result_field": field_name,
                }
            )

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


class ChoiceDirective(SphinxDirective):
    """Render a generic single-choice group outside a test case."""

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "id": directives.unchanged,
        "class": directives.unchanged,
    }

    def run(self):
        field_id = self.options.get("id", "").strip()
        if not field_id:
            raise self.error("test:choice requires an :id: option")

        options = [line.strip() for line in self.content if line.strip()]
        if len(options) < 2:
            raise self.error("test:choice requires at least two non-empty option lines")

        field_name = free_radio_field_name(field_id, self.env.docname)
        html = free_radio_control_html(
            self.arguments[0],
            field_name,
            options,
            self.options.get("class", ""),
        )
        return [nodes.raw("", html, format="html")]


class CommentDirective(SphinxDirective):
    """Render a generic multiline annotation field outside a test case."""

    has_content = False
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "id": directives.unchanged,
        "rows": directives.positive_int,
        "class": directives.unchanged,
    }

    def run(self):
        field_id = self.options.get("id", "").strip()
        if not field_id:
            raise self.error("test:comment requires an :id: option")

        field_name = free_comment_field_name(field_id, self.env.docname)
        html = free_comment_control_html(
            self.arguments[0],
            field_name,
            self.options.get("rows", 4),
            self.options.get("class", ""),
        )
        return [nodes.raw("", html, format="html")]


class FileListDirective(SphinxDirective):
    has_content = False
    required_arguments = 0
    option_spec = {
        "filter": directives.unchanged,
        "class": directives.unchanged,
    }

    def run(self):
        logger.debug("adding test filelist")
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
            for k, _v in _files.items():
                _content.append(k)

        if "class" in self.options:
            _classes.append(self.options["class"])

        listnode = nodes.bullet_list(classes=_classes)
        for entry in _content:
            listnode += nodes.list_item("", nodes.Text(entry), classes=["test-filelist-item"])

        return [listnode]
