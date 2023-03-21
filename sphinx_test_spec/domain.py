import types
from collections import defaultdict
from pathlib import PurePosixPath

from docutils.nodes import Node, system_message
from docutils.parsers.rst import nodes
from sphinx.domains import Domain, Index
from sphinx.locale import get_translation
from sphinx.roles import EmphasizedLiteral, XRefRole
from sphinx.util import logging, ws_re
from sphinx.util.nodes import make_refnode

MESSAGE_CATALOG_NAME = "sphinx_test_spec"
_ = get_translation(MESSAGE_CATALOG_NAME)

from sphinx_test_spec.directives import (  # ColumnDirective,; RowDirective,; TableDirective,
    ActionDirective,
    FileListDirective,
    ReactionDirective,
    TestCaseDirective,
)

logger = logging.getLogger(__name__)


class TestSpecIndex(Index):
    """A custom index that creates an table matrix."""

    name = "test"
    localname = _("Test Specification Index")
    shortname = _("Test Specs")

    def generate(self, docnames=None):
        content = defaultdict(list)

        # sort the list of test specs in alphabetical order
        test_specs = self.domain.get_objects()
        test_specs = sorted(test_specs, key=lambda test_spec: test_spec[0])

        # generate the expected output, shown below, from the above using the
        # first letter of the recipe as a key to group thing
        #
        # name, subtype, docname, anchor, extra, qualifier, description
        for _name, dispname, typ, docname, anchor, _priority in test_specs:
            content[dispname[0].lower()].append((dispname, 0, docname, anchor, docname, "", typ))

        # convert the dict to the sorted list of tuples expected
        content = sorted(content.items())

        return content, True


# class ActionRole(XRefRole):
#
#    def result_nodes(self, document, env, node, is_ref):
#        """Called before returning the finished nodes.  *node* is the reference
#        node if one was created (*is_ref* is then true), else the content node.
#        This method can add other nodes and must return a ``(nodes, messages)``
#        tuple (the usual return value of a role function).
#        """
#        return super().result_nodes(document,env,node, is_ref)
#
#    def process_link(self, env, refnode, has_explicit_title, title, target):
#        """Called after parsing title and target text, and creating the
#        reference node (given in *refnode*).  This method can alter the
#        reference node and must return a new (or the same) ``(title, target)``
#        tuple.
#        """
#        #print(f"parsing Actionrole: {title}, {target}")
#
#        return super().process_link(env,refnode,has_explicit_title,title,target)


class FileRole(EmphasizedLiteral):
    def run(self) -> tuple[list[Node], list[system_message]]:
        (nodes, message) = super().run()
        test_domain = self.env.get_domain("test")
        test_domain.add_file(self.text)

        return (nodes, message)


class TestSpecDomain(Domain):

    name = "test"
    label = "Test Specifications"
    roles = {"case": XRefRole(), "action": XRefRole(), "file": FileRole()}

    directives = {
        "case": TestCaseDirective,
        "action": ActionDirective,
        "reaction": ReactionDirective,
        "filelist": FileListDirective,
    }

    indices = {TestSpecIndex}
    # indices = {}

    initial_data = {
        "cases": [],  # list of all test cases for references
        "actions": [],  # list of all test actions for references
        "state": types.SimpleNamespace(
            cases={},
            actions={},
            case_id=0,
            action_id=0,
            node_reaction=None,
            node_table=None,
            node_table_id=None,
            node_tgroup=None,
            node_tbody=None,
            node_thead=None
            # , node_colspec = None
            ,
            action_anchor=None,
            columns=4,
            headers=["id", "action", "reaction", "ok"],
        ),  # internal parser state
        "files": {},  # dictionary of mentioned test files
    }

    #    def setup(self):
    #        super().setup()
    #        self._state.case_id = 0

    def get_full_qualified_name(self, node):
        return "{}.{}".format("test_case", node.arguments[0])

    def get_objects(self):
        for obj in self.data["cases"]:
            yield (obj)
        for obj in self.data["actions"]:
            yield (obj)

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        match = [
            (docname, anchor, sig) for name, sig, typ, docname, anchor, prio in self.get_objects() if target in anchor
        ]

        if len(match) > 0:
            todocname = match[0][0]
            targ = match[0][1]
            tdispname = match[0][2]

            if typ == "action":
                targ = f"test-action-{targ}"
                classes = []

                if contnode.hasattr("classes"):
                    classes = contnode.attributes["classes"]
                contnode = nodes.literal(text=f"{tdispname}", classes=classes)
            elif typ == "case":
                targ = f"test-case-{targ}"

            # print(f"adding refnode targetid {targ}, target={target}, contnone={contnode}")

            return make_refnode(builder, fromdocname, todocname, targ, contnode)
        else:
            logger.debug(f"Could not resolve xref for {target}")
            return None

    def add_case(self, signature):  # , id):
        """Add a new test case to the domain."""
        for _id in [signature]:  # , id]:
            if _id is not None:
                name = "{}.{}".format("test-case", _id)
                # anchor = "test-case-{}".format(_id)
                anchor = _id

                # name, dispname, type, docname, anchor, priority
                logger.debug(f"adding referency to test specifications: {name}, {_id}, {anchor}")
                self.data["cases"].append((name, _id, "Test Case", self.env.docname, anchor, 0))

    def add_action(self, case_id, action_id, signature):
        """Add a new test action to the domain."""
        name = "{}.{}".format("test-action", action_id)
        # anchor = "test-action-{}".format(action_id)
        anchor = f"{case_id}.{action_id}"

        # name, dispname, type, docname, anchor, priority
        logger.debug(f"adding referency to action: {name}, {action_id}, {anchor}, {signature}")
        # print(f"adding reference to action: {name}, {action_id}, {anchor}, {signature}")
        self.data["actions"].append((name, signature, "Test Action", self.env.docname, anchor, 0))

    def add_file(self, name):
        path = PurePosixPath(name)
        self.data["files"][str(path)] = {"name": path.name, "path": path.parent, "suffix": path.suffix}
