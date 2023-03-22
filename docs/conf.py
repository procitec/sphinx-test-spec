# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'sphinx-test-spec'
copyright = '2022, team procitec'
author = 'team procitec'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_immaterial'
#    'sphinx.ext.autosectionlabel'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_immaterial'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

html_sidebars = {'**': ['about.html', 'navigation.html', 'searchbox.html'], }

#html_theme_options = {
    ## 'description': "an extension for sphinx",
    #'logo_text_align': "center",
    #'github_user': 'procitec',
    #'github_repo': 'sphinx-test-spec',
    #'github_banner': True,
    #'github_button': True,
    #'github_type': 'star',
    #'fixed_sidebar': True,
    #'extra_nav_links': {
                        #'sphinx-test-spec@github': "https://github.com/procitec/sphinx-test-spec",
                        #}
#}


html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
    },
    "site_url": "https://github.com/procitec/sphinx-test-spec",
    "repo_url": "https://github.com/procitec/sphinx-test-spec",
    "repo_name": "sphinx-test-spec",
    "repo_type": "github",
    "edit_uri": "blob/master/docs",
    # "google_analytics": ["UA-XXXXX", "auto"],
    "globaltoc_collapse": True,
    "features": [
        "navigation.sections",
        "navigation.top",
        "search.share",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "blue",
            "accent": "light-blue",
            "toggle": {
                "icon": "material/weather-night",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "blue",
            "accent": "yellow",
            "toggle": {
                "icon": "material/weather-sunny",
                "name": "Switch to light mode",
            },
        },
    ],
    "toc_title_is_page_title": True,
}
