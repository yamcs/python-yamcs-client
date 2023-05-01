import pkg_resources

project = "yamcs-client"
copyright = "2020, Space Applications Services"
author = "Space Applications Services"
version = ""
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
templates_path = ["_templates"]

dist = pkg_resources.get_distribution("yamcs-client")
release = dist.version

extensions = [
    # We don't use napolean style, but keep this because it suppresses
    # erros coming from docstring when Future is inherited.
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.fulltoc",
]

html_theme = "alabaster"
html_theme_options = {
    "description": "Yamcs Client Library for Python",
    "fixed_sidebar": False,
    "show_powered_by": False,
    "font_family": "Helvetica,Arial,sans-serif",
    "font_size": "15px",
}
html_static_path = ["_static"]
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        # located at _templates/
        "projectlinks.html",
    ]
}

html_show_sourcelink = False


latex_elements = {
    "papersize": "a4paper",
    "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        f"python-yamcs-client-{release}.tex",
        "Python Yamcs Client",
        "Space Applications Services",
        "manual",
    ),
]

# Too many URLs (for each datatype), so hide them
latex_show_urls = "no"
latex_show_pagerefs = False

autoclass_content = "both"

intersphinx_mapping = {
    "requests": ("https://requests.kennethreitz.org/en/stable/", None),
    "python": ("https://docs.python.org/3", None),
}


def setup(app):
    app.add_css_file("css-overrides.css")
