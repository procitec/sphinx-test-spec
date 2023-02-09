pybabel extract --output=sphinx_test_spec/locales/sphinx_test_spec.pot sphinx_test_spec
pybabel init --input-file=sphinx_test_spec/locales/sphinx_test_spec.pot --domain=sphinx_test_spec --output-dir=sphinx_test_spec/locales --locale=de_DE
pybabel init --input-file=sphinx_test_spec/locales/sphinx_test_spec.pot --domain=sphinx_test_spec --output-dir=sphinx_test_spec/locales --locale=en_US
pybabel update --input-file=sphinx_test_spec/locales/sphinx_test_spec.pot --domain=sphinx_test_spec --output-dir=sphinx_test_spec/locales
pybabel compile --directory=sphinx_test_spec/locales --domain=sphinx_test_spec
