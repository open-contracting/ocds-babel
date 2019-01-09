import csv
import gettext
import json
import logging
import os
from collections import OrderedDict
from copy import deepcopy
from io import StringIO

from docutils.frontend import OptionParser
from docutils.io import InputError
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document, SystemMessage
from recommonmark.parser import CommonMarkParser
from recommonmark.transform import AutoStructify
from sphinx.application import Sphinx

from ocds_babel import TRANSLATABLE_CODELIST_HEADERS, TRANSLATABLE_SCHEMA_KEYWORDS, TRANSLATABLE_EXTENSION_METADATA_KEYWORDS  # noqa: E501
from ocds_babel.directives import NullDirective
from ocds_babel.markdown_translator import MarkdownTranslator
from ocds_babel.util import text_to_translate

logger = logging.getLogger('ocds_babel')


def translate(configuration, localedir, language, **kwargs):
    """
    Writes files, translating any translatable strings.

    For translated strings in schema files, replaces `{{lang}}` with the language code. Keyword arguments may specify
    additional replacements.
    """
    translators = {}

    for sources, target, domain in configuration:
        logger.info('Translating to {} using "{}" domain, into {}'.format(language, domain, target))

        if domain not in translators:
            translators[domain] = gettext.translation(
                domain, localedir, languages=[language], fallback=language == 'en')

        os.makedirs(target, exist_ok=True)

        for source in sources:
            basename = os.path.basename(source)
            with open(source) as r, open(os.path.join(target, basename), 'w') as w:
                if source.endswith('.csv'):
                    method = translate_codelist
                elif source.endswith('-schema.json'):
                    method = translate_schema
                    kwargs.update(lang=language)
                elif source.endswith('.md'):
                    method = translate_markdown
                elif basename == 'extension.json':
                    method = translate_extension_metadata
                    kwargs.update(lang=language)
                else:
                    raise NotImplementedError(basename)
                w.write(method(r, translators[domain], **kwargs))


# This should roughly match the logic of `extract_codelist`.
def translate_codelist(io, translator, **kwargs):
    """
    Accepts a CSV file as an IO object, and returns its translated contents in CSV format.
    """
    reader = csv.DictReader(io)

    fieldnames = [translator.gettext(fieldname) for fieldname in reader.fieldnames]
    rows = translate_codelist_data(reader, translator, **kwargs)

    io = StringIO()
    writer = csv.DictWriter(io, fieldnames, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

    return io.getvalue()


def translate_codelist_data(source, translator, **kwargs):
    """
    Accepts CSV rows as an iterable object (e.g. a list of dictionaries), and returns translated rows.
    """
    rows = []
    for row in source:
        data = {}
        for key, value in row.items():
            text = text_to_translate(value, key in TRANSLATABLE_CODELIST_HEADERS)
            if text:
                value = translator.gettext(text)
            data[translator.gettext(key)] = value
        rows.append(data)
    return rows


# This should roughly match the logic of `extract_schema`.
def translate_schema(io, translator, **kwargs):
    """
    Accepts a JSON file as an IO object, and returns its translated contents in JSON format.
    """
    data = json.load(io, object_pairs_hook=OrderedDict)

    data = translate_schema_data(data, translator, **kwargs)

    return json.dumps(data, indent=2, separators=(',', ': '), ensure_ascii=False)


def translate_schema_data(source, translator, **kwargs):
    """
    Accepts JSON data, and returns translated data.
    """
    def _translate_schema_data(data):
        if isinstance(data, list):
            for item in data:
                _translate_schema_data(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                _translate_schema_data(value)
                text = text_to_translate(value, key in TRANSLATABLE_SCHEMA_KEYWORDS)
                if text:
                    data[key] = translator.gettext(text)
                    for old, new in kwargs.items():
                        data[key] = data[key].replace('{{' + old + '}}', new)

    data = deepcopy(source)
    _translate_schema_data(data)
    return data


# This should roughly match the logic of `extract_extension_metadata`.
def translate_extension_metadata(io, translator, lang='en', **kwargs):
    """
    Accepts an extension metadata file as an IO object, and returns its translated contents in JSON format.
    """
    data = json.load(io, object_pairs_hook=OrderedDict)

    data = translate_extension_metadata_data(data, translator, lang, **kwargs)

    return json.dumps(data, indent=2, separators=(',', ': '), ensure_ascii=False)


def translate_extension_metadata_data(source, translator, lang='en', **kwargs):
    """
    Accepts extension metadata, and returns translated metadata.
    """
    data = deepcopy(source)

    for key in TRANSLATABLE_EXTENSION_METADATA_KEYWORDS:
        value = data.get(key)

        if isinstance(value, dict):
            value = value.get('en')

        text = text_to_translate(value)
        if text:
            data[key] = {lang: translator.gettext(text)}

    return data


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

    # sphinx-build -b html -q -E …
    app = Sphinx('.', None, '.', '.', 'html', status=None, freshenv=True)
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
