import csv
import gettext
import json
import logging
import os
from collections import OrderedDict
from io import StringIO

from docutils.utils import new_document
from recommonmark.parser import CommonMarkParser

from ocds_babel import TRANSLATABLE_CODELIST_HEADERS, TRANSLATABLE_SCHEMA_KEYWORDS, TRANSLATABLE_EXTENSION_METADATA_KEYWORDS  # noqa: E501
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
                    kwargs = dict(lang=language, **kwargs)
                elif source.endswith('.md'):
                    method = translate_markdown
                elif basename == 'extension.json':
                    method = translate_extension_metadata
                    kwargs = dict(lang=language, **kwargs)
                else:
                    raise NotImplementedError(basename)
                w.write(method(r, translators[domain], **kwargs))


# This should roughly match the logic of `extract_codelist`.
def translate_codelist(io, translator, **kwargs):
    reader = csv.DictReader(io)

    fieldnames = [translator.gettext(fieldname) for fieldname in reader.fieldnames]

    rows = []
    for row in reader:
        data = {}
        for key, value in row.items():
            text = text_to_translate(value, key in TRANSLATABLE_CODELIST_HEADERS)
            if text:
                value = translator.gettext(text)
            data[translator.gettext(key)] = value
        rows.append(data)

    io = StringIO()
    writer = csv.DictWriter(io, fieldnames, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

    return io.getvalue()


# This should roughly match the logic of `extract_schema`.
def translate_schema(io, translator, **kwargs):
    def _translate_schema(data):
        if isinstance(data, list):
            for item in data:
                _translate_schema(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                _translate_schema(value)
                text = text_to_translate(value, key in TRANSLATABLE_SCHEMA_KEYWORDS)
                if text:
                    data[key] = translator.gettext(text)
                    for old, new in kwargs.items():
                        data[key] = data[key].replace('{{' + old + '}}', new)

    data = json.load(io, object_pairs_hook=OrderedDict)

    _translate_schema(data)

    return json.dumps(data, indent=2, separators=(',', ': '), ensure_ascii=False)


# This should roughly match the logic of `extract_extension_metadata`.
def translate_extension_metadata(io, translator, lang='en', **kwargs):
    data = json.load(io, object_pairs_hook=OrderedDict)

    for key in TRANSLATABLE_EXTENSION_METADATA_KEYWORDS:
        value = data.get(key)

        if isinstance(value, dict):
            value = value.get('en')

        text = text_to_translate(value)
        if text:
            data[key] = {lang: translator.gettext(text)}

    return json.dumps(data, indent=2, separators=(',', ': '), ensure_ascii=False)


def translate_markdown(io, translator, settings=None, **kwargs):
    text = io.read()

    document = new_document(io.name, settings)
    CommonMarkParser().parse(text, document)
    visitor = MarkdownTranslator(document, translator)
    document.walkabout(visitor)

    return visitor.astext()
