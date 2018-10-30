"""
`Babel extractors <http://babel.pocoo.org/en/latest/messages.html>`__ for codelist CSV files and JSON Schema files.
"""

import csv
import json
import os
from io import StringIO

from ocds_babel import TRANSLATABLE_CODELIST_HEADERS, TRANSLATABLE_SCHEMA_KEYWORDS, TRANSLATABLE_EXTENSION_METADATA_KEYWORDS  # noqa: E501


def extract_codelist(fileobj, keywords, comment_tags, options):
    """
    Yields each header, and the Title, Description and Extension values of a codelist CSV file.
    """

    # standard-maintenance-scripts validates the headers of codelist CSV files.
    reader = csv.DictReader(StringIO(fileobj.read().decode()))
    for header in reader.fieldnames:
        yield 0, '', header, ''

    # Don't translate the titles of the hundreds of currencies.
    if os.path.basename(fileobj.name) != 'currency.csv':
        for lineno, row in enumerate(reader, 1):
            for key, value in row.items():
                if key in TRANSLATABLE_CODELIST_HEADERS and isinstance(value, str):
                    value = value.strip()
                    if value:
                        yield lineno, '', value, [key]


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
                if key in TRANSLATABLE_SCHEMA_KEYWORDS and isinstance(value, str):
                    value = value.strip()
                    if value:
                        yield value, '{}/{}'.format(pointer, key)
                yield from _extract_schema(value, pointer='{}/{}'.format(pointer, key))

    data = json.loads(fileobj.read().decode())
    for text, pointer in _extract_schema(data):
        yield 1, '', text, [pointer]


def extract_extension_metadata(fileobj, keywords, comment_tags, options):
    """
    Yields the "name" and "description" values of an extension.json file.
    """
    data = json.loads(fileobj.read().decode())
    for key in TRANSLATABLE_EXTENSION_METADATA_KEYWORDS:
        comment = '/' + key
        value = data.get(key, {})

        # Add language map.
        if isinstance(value, dict):
            comment += '/en'
        else:
            value = {'en': value}

        value = value.get('en', '').strip()
        if value:
            yield 1, '', value, [comment]
