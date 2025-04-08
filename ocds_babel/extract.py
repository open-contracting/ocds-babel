"""
Babel extractors can be specified in configuration files.

For OCDS, you can specify::

    [ocds_codelist: schema/*/codelists/*.csv]
    headers = Title,Description,Extension
    ignore = currency.csv

in ``babel_ocds_codelist.cfg``, and::

    [ocds_schema: schema/*/*-schema.json]

in ``babel_ocds_schema.cfg``.

For BODS, you can specify::

    [ocds_codelist: schema/codelists/*.csv]
    headers = title,description,technical note

in ``babel_bods_codelist.cfg``, and::

    [ocds_schema: schema/*.json]

in ``babel_bods_schema.cfg``.

For OC4IDS, you can specify::

    [oc4ids_sustainability_mapping: mapping/sustainability.yaml]
    keys = title,disclosure format,mapping

in ``babel_oc4ids_sustainability_mapping.cfg``.
"""

import csv
import json
import os
from io import StringIO

import yaml

from ocds_babel import TRANSLATABLE_EXTENSION_METADATA_KEYWORDS, TRANSLATABLE_SCHEMA_KEYWORDS
from ocds_babel.util import text_to_translate


def extract_codelist(fileobj, keywords, comment_tags, options):
    """Yield each header, and the specified field values of a codelist CSV file."""
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
    """Yield the "title" and "description" values of a JSON Schema file."""
    def _extract_schema(data, pointer=''):
        if isinstance(data, list):
            for index, item in enumerate(data):
                yield from _extract_schema(item, pointer=f'{pointer}/{index}')
        elif isinstance(data, dict):
            for key, value in data.items():
                yield from _extract_schema(value, pointer=f'{pointer}/{key}')
                text = text_to_translate(value, key in TRANSLATABLE_SCHEMA_KEYWORDS)
                if text:
                    yield text, f'{pointer}/{key}'

    data = json.loads(fileobj.read().decode())
    for text, pointer in _extract_schema(data):
        yield 1, '', text, [pointer]


def extract_extension_metadata(fileobj, keywords, comment_tags, options):
    """Yield the "name" and "description" values of an extension.json file."""
    data = json.loads(fileobj.read().decode())
    for key in TRANSLATABLE_EXTENSION_METADATA_KEYWORDS:
        value = data.get(key)

        if isinstance(value, dict):
            comment = f'/{key}/en'
            value = value.get('en')
        else:
            # old extension.json format
            comment = f'/{key}'

        text = text_to_translate(value)
        if text:
            yield 1, '', text, [comment]


def extract_yaml(fileobj, keywords, comment_tags, options):
    """Yield the values of the specified keys of a YAML file."""
    keys = _get_option_as_list(options, 'keys')
    def _extract_yaml(data, pointer=''):
        if isinstance(data, list):
            for index, item in enumerate(data):
                yield from _extract_yaml(item, pointer=f'{pointer}/{index}')
        elif isinstance(data, dict):
            for key, value in data.items():
                yield from _extract_yaml(value, pointer=f'{pointer}/{key}')
                text = text_to_translate(value, key in keys)
                if text:
                    yield text, f'{pointer}/{key}'

    data = yaml.safe_load(fileobj.read().decode())

    for text, pointer in _extract_yaml(data):
        yield 1, '', text, [pointer]


def _get_option_as_list(options, key):
    if options:
        return options.get(key, '').split(',')
    return []
