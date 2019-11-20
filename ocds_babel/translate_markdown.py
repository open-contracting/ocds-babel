import logging
from contextlib import contextmanager

import sphinx
from docutils.frontend import OptionParser
from docutils.io import InputError
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document, SystemMessage
from recommonmark.parser import CommonMarkParser
from recommonmark.transform import AutoStructify
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from ocds_babel.directives import NullDirective
from ocds_babel.markdown_translator import MarkdownTranslator

# patch_docutils is added in Sphinx 1.6.
if sphinx.version_info >= (1, 6):
    from sphinx.util.docutils import patch_docutils
else:
    @contextmanager
    def patch_docutils(confdir=None):
        yield

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

    with patch_docutils(), docutils_namespace():
        # sphinx-build -b html -q -E …
        app = Sphinx('.', None, 'outdir', '.', 'html', status=None, freshenv=True)
        # Avoid "recommonmark_config not setted, proceed default setting".
        app.add_config_value('recommonmark_config', {}, True)

        # From code comment in `new_document`.
        settings = OptionParser(components=(Parser,)).get_default_values()
        # Get minimal settings for `AutoStructify` to be applied.
        settings.env = app.builder.env

        document = new_document(name, settings)
        CommonMarkParser().parse(text, document)

        # To translate messages in `.. list-table`.
        try:
            AutoStructify(document).apply()
        except SystemMessage as e:
            context = e.__context__
            if isinstance(context, InputError) and context.strerror == 'No such file or directory':  # csv-table
                logger.warning(e)

        visitor = MarkdownTranslator(document, translator)
        document.walkabout(visitor)

        return visitor.astext()
