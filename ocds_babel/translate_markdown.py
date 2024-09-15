from markdown_it import MarkdownIt
from mdformat.renderer import MDRenderer


def translate_markdown(io, translator, **kwargs):
    """Accept a Markdown file as an IO object, and return its translated contents in Markdown format."""
    name = io.name
    text = io.read()

    return translate_markdown_data(name, text, translator, **kwargs)


def translate_markdown_data(name, md, translator, **kwargs):
    """Accept a Markdown file as its filename and contents, and return its translated contents in Markdown format."""
    parser = MarkdownIt()
    env = {}

    tokens = []
    for token in parser.parse(md, env):
        if token.type == 'inline':
            new_token = parser.parse(translator.gettext(token.content))[1]
            new_token.level = token.level
            tokens.append(new_token)
        else:
            tokens.append(token)

    return MDRenderer().render(tokens, parser.options, env)
