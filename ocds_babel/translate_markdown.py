import logging

from docutils.parsers.rst import directives
from myst_parser.main import to_docutils

from ocds_babel.directives import NullDirective
from ocds_babel.markdown_translator import MarkdownTranslator

logger = logging.getLogger('ocds_babel')


def translate_markdown(io, translator, **kwargs):
    """
    Accepts a Markdown file as an IO object, and returns its translated contents in Markdown format.
    """
    name = io.name
    text = io.read()

    return translate_markdown_data(name, text, translator, **kwargs)


def translate_markdown_data(name, text, translator, **kwargs):
    """
    Accepts a Markdown file as its filename and contents, and returns its translated contents in Markdown format.
    """
    # This only needs to be run once, but is inexpensive.
    for directive_name in ('csv-table-no-translate', 'extensiontable'):
        directives.register_directive(directive_name, NullDirective)

    document = to_docutils(text, in_sphinx_env=True)

    visitor = MarkdownTranslator(document, translator)
    document.walkabout(visitor)

    return visitor.astext()
