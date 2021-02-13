from myst_parser.main import to_docutils

from ocds_babel.markdown_translator import MarkdownTranslator


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
    document = to_docutils(text, in_sphinx_env=True)

    visitor = MarkdownTranslator(document, translator)
    document.walkabout(visitor)

    return visitor.astext()
