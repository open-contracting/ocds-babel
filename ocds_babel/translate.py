import csv
import gettext
import glob
import json
import logging
import os
from collections import OrderedDict
from io import StringIO

from ocds_babel import TRANSLATABLE_CODELIST_HEADERS, TRANSLATABLE_SCHEMA_KEYWORDS, TRANSLATABLE_EXTENSION_METADATA_KEYWORDS  # noqa: E501
from ocds_babel.util import text_to_translate

logger = logging.getLogger('ocds_babel')


def translations_instance(domain, localedir, language):
    return gettext.translation(domain, localedir, languages=[language], fallback=language == 'en')


def translate_codelists(domain, sourcedir, builddir, localedir, language):
    """
    Writes files, translating each header and the Title, Description and Extension values of codelist CSV files.

    These files are typically referenced by `csv-table-no-translate` directives.

    Args:

    * domain: The gettext domain.
    * sourcedir: The path to the directory containing the codelist CSV files.
    * builddir: The path to the build directory.
    * localedir: The path to the `locale` directory.
    * language: A two-letter lowercase ISO369-1 code or BCP47 language tag.
    """
    logger.info('Translating codelists to {} using "{}" domain, from {} to {}'.format(
        language, domain, sourcedir, builddir))

    translator = translations_instance(domain, localedir, language)

    os.makedirs(builddir, exist_ok=True)

    for file in glob.glob(os.path.join(sourcedir, '*.csv')):
        with open(file) as r, open(os.path.join(builddir, os.path.basename(file)), 'w') as w:
            w.write(translate_codelist_from_io(r, translator))


def translate_schema(domain, filenames, sourcedir, builddir, localedir, language, **kwargs):
    """
    Writes files, translating the "title" and "description" values of JSON Schema files.

    In translated strings, replaces `{{lang}}` with the language code. Keyword arguments specify more replacements.

    These files are typically referenced by `jsonschema` directives.

    Args:

    *  domain: The gettext domain.
    *  filenames: A list of JSON Schema filenames to translate.
    *  sourcedir: The path to the directory containing the JSON Schema files.
    *  builddir: The path to the build directory.
    *  localedir: The path to the `locale` directory.
    *  language: A two-letter lowercase ISO369-1 code or BCP47 language tag.
    """
    logger.info('Translating schemas to {} using "{}" domain, from {} to {}'.format(
        language, domain, sourcedir, builddir))

    translator = translations_instance(domain, localedir, language)

    for name in filenames:
        os.makedirs(os.path.dirname(os.path.join(builddir, name)), exist_ok=True)

        with open(os.path.join(sourcedir, name)) as r, open(os.path.join(builddir, name), 'w') as w:
            w.write(translate_schema_from_io(r, translator, dict(lang=language, **kwargs)))


def translate_extension_metadata(domain, sourcedir, builddir, localedir, language):
    translator = translations_instance(domain, localedir, language)

    os.makedirs(builddir, exist_ok=True)

    with open(os.path.join(sourcedir, 'extension.json')) as r, open(os.path.join(builddir, 'extension.json'), 'w') as w:  # noqa: E501
        w.write(translate_extension_metadata_from_io(r, translator, language))


# This should roughly match the logic of `extract_codelist`.
def translate_codelist_from_io(io, translator):
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
def translate_schema_from_io(io, translator, replacements={}):
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
                    for old, new in replacements.items():
                        data[key] = data[key].replace('{{' + old + '}}', new)

    data = json.load(io, object_pairs_hook=OrderedDict)

    _translate_schema(data)

    return json.dumps(data, indent=2, separators=(',', ': '), ensure_ascii=False)


# This should roughly match the logic of `extract_extension_metadata`.
def translate_extension_metadata_from_io(io, translator, language='en'):
    data = json.load(io, object_pairs_hook=OrderedDict)

    for key in TRANSLATABLE_EXTENSION_METADATA_KEYWORDS:
        value = data.get(key)

        if isinstance(value, dict):
            value = value.get('en')

        text = text_to_translate(value)
        if text:
            data[key] = {language: translator.gettext(text)}

    return json.dumps(data, indent=2, separators=(',', ': '), ensure_ascii=False)
