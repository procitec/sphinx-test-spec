extensions = ["sphinx_test_spec"]

project = "Manual application tests"
master_doc = "index"

testspec_result_mode = "form"
testspec_namespace = "category.appname"
testspec_document_id = "application-manual-test"
testspec_header = ["Nr.", "Action", "Reaction", ""]
testspec_header_widths = [6, 45, 42, 7]
testspec_result_labels = {
    "passed": "✓",
    "failed": "✗",
    "na": "–",
}
testspec_comment_label = "Anmerkung"
