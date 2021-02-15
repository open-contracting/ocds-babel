from markdown_it import MarkdownIt
from mdformat.renderer import MDRenderer


def translate_markdown(io, translator, **kwargs):
    """
    Accepts a Markdown file as an IO object, and returns its translated contents in Markdown format.
    """
    name = io.name
    text = io.read()

    return translate_markdown_data(name, text, translator, **kwargs)


def translate_markdown_data(name, md, translator, **kwargs):
    """
    Accepts a Markdown file as its filename and contents, and returns its translated contents in Markdown format.
    """
    parser = MarkdownIt()

    tokens = []
    for token in parser.parse(md):
        if token.type == 'inline':
            tokens.extend(parser.parse(translator.gettext(token.content))[1:-1])
        else:
            tokens.append(token)

    return MDRenderer().render(tokens, {}, {})
