import csv
import json
import os
from io import StringIO

from ocds_babel import TRANSLATABLE_SCHEMA_KEYWORDS, TRANSLATABLE_EXTENSION_METADATA_KEYWORDS  # noqa: E501
from ocds_babel.util import text_to_translate


def extract_codelist(fileobj, keywords, comment_tags, options):
    """
    Yields each header, and the specified field values of a codelist CSV file.
    """
    headers = _get_option_as_list(options, 'headers')
    ignore = _get_option_as_list(options, 'ignore')

    # Use universal newlines mode, to avoid parsing errors.
    reader = csv.DictReader(StringIO(fileobj.read().decode(), newline=''))
    for fieldname in reader.fieldnames:
        if fieldname:
            yield 0, '', fieldname, ''

    if os.path.basename(fileobj.name) not in ignore:
        for lineno, row in enumerate(reader, 1):
            for key, value in row.items():
                text = text_to_translate(value, key in headers)
                if text:
                    yield lineno, '', text, [key]


def extract_schema(fileobj, keywords, comment_tags, options):
    """
    Yields the "title" and "description" values of a JSON Schema file.
    """
    def _extract_schema(data, pointer=''):
        if isinstance(data, list):
            for index, item in enumerate(data):
                yield from _extract_schema(item, pointer='{}/{}'.format(pointer, index))
        elif isinstance(data, dict):
            for key, value in data.items():
                yield from _extract_schema(value, pointer='{}/{}'.format(pointer, key))
                text = text_to_translate(value, key in TRANSLATABLE_SCHEMA_KEYWORDS)
                if text:
                    yield text, '{}/{}'.format(pointer, key)

    data = json.loads(fileobj.read().decode())
    for text, pointer in _extract_schema(data):
        yield 1, '', text, [pointer]


def extract_extension_metadata(fileobj, keywords, comment_tags, options):
    """
    Yields the "name" and "description" values of an extension.json file.
    """
    data = json.loads(fileobj.read().decode())
    for key in TRANSLATABLE_EXTENSION_METADATA_KEYWORDS:
        value = data.get(key)

        if isinstance(value, dict):
            comment = '/{}/en'.format(key)
            value = value.get('en')
        else:
            # old extension.json format
            comment = '/{}'.format(key)

        text = text_to_translate(value)
        if text:
            yield 1, '', text, [comment]


def _get_option_as_list(options, key):
    if options:
        return options.get(key, '').split(',')
    return []
