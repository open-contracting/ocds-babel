from mdformat import text


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
    return text(md, options={"translator": translator})
