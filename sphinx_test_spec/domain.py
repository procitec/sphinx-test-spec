from collections import defaultdict

from sphinx.domains import Domain, Index
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.nodes import make_refnode

from sphinx.locale import get_translation

MESSAGE_CATALOG_NAME = 'sphinx_test_spec'
_ = get_translation(MESSAGE_CATALOG_NAME)

from sphinx_test_spec.directives import (
    TestCaseDirective,
    ActionDirective,
    ReactionDirective
    #ColumnDirective,
    #RowDirective,
    #TableDirective,
)

logger = logging.getLogger(__name__)


class TestSpecIndex(Index):
    """A custom index that creates an table matrix."""

    name = "test"
    localname = _('Test Specification Index')
    shortname = _('Test Specs')

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


class TestSpecDomain(Domain):

    name = "test"
    label = "Test Specifications"
    roles = {"tbl": XRefRole(), "row": XRefRole()}
    #roles = {}

    directives = {
        "case": TestCaseDirective,
        "action": ActionDirective,
        "reaction": ReactionDirective,
    }

    #indices = {TestSpecIndex}
    indices = {}

    initial_data = {
        "test_cases": [],  # object list
#        "actions": [],  # object list
    }

    def get_full_qualified_name(self, node):
        return "{}.{}".format("test_case", node.arguments[0])

    def get_objects(self):
        for obj in self.data["test_cases"]:
            yield (obj)
        #for obj in self.data["actions"]:
        #    yield (obj)

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        match = [(docname, anchor) for name, sig, typ, docname, anchor, prio in self.get_objects() if sig == target]

        if len(match) > 0:
            todocname = match[0][0]
            targ = match[0][1]

            return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
        else:
            logger.debug(f"Could not resolve xref for {target}")
            return None

    def add_case(self, signature, id):
        """Add a new test case to the domain."""
        for _id in [signature, id]:
            if _id is not None:
                name = "{}.{}".format("test-case", _id)
                anchor = "test-case-{}".format(_id)

                # name, dispname, type, docname, anchor, priority
                logger.debug(f"adding referency to test specifications: {name}, {_id}, {anchor}")
                self.data["test_cases"].append((name, _id, "Test Case", self.env.docname, anchor, 0))

    #def add_action(self, index_entry):
    #    """Add a new test action to the domain."""
    #    name = "{}.{}".format("action", index_entry)
    #    anchor = "action-{}".format(index_entry)

    #    # name, dispname, type, docname, anchor, priority
    #    logger.debug(f"adding referency to action: {name}, {index_entry}, {anchor}")
    #    self.data["actions"].append((name, index_entry, "Action", self.env.docname, anchor, 0))
