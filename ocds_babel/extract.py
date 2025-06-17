"""
Babel extractors can be specified in configuration files.

For OCDS, you can specify in ``babel_ocds_codelist.cfg``::

    [ocds_codelist: schema/*/codelists/*.csv]
    headers = Title,Description,Extension
    ignore = currency.csv

and in ``babel_ocds_schema.cfg``::

    [ocds_schema: schema/*/*-schema.json]

For BODS, you can specify in ``babel_bods_codelist.cfg``::

    [ocds_codelist: schema/codelists/*.csv]
    headers = title,description,technical note

and in ``babel_bods_schema.cfg``::

    [ocds_schema: schema/*.json]

For OC4IDS, you can specify in a Babel ``.cfg`` file::

    [extractors]
    yaml = ocds_babel.extract:extract_yaml
    [yaml: mapping/sustainability.yaml]
    keys = title,disclosure format,mapping
"""

import csv
import json
import os
from io import StringIO

from ocds_babel import TRANSLATABLE_EXTENSION_METADATA_KEYWORDS, TRANSLATABLE_SCHEMA_KEYWORDS
from ocds_babel.util import text_to_translate


def extract_codelist(fileobj, keywords, comment_tags, options):
    """Yield each header, and the values of the specified fields of a codelist CSV file."""
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
    def _extract_schema(data, pointer):
        if isinstance(data, list):
            for index, item in enumerate(data):
                yield from _extract_schema(item, pointer=f'{pointer}/{index}')
        elif isinstance(data, dict):
            for key, value in data.items():
                new_pointer = f'{pointer}/{key}'
                yield from _extract_schema(value, pointer=new_pointer)
                text = text_to_translate(value, key in TRANSLATABLE_SCHEMA_KEYWORDS)
                if text:
                    yield 1, '', text, [new_pointer]

    yield from _extract_schema(json.loads(fileobj.read().decode()), '')


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
    import yaml  # noqa: PLC0415

    keys = _get_option_as_list(options, 'keys')

    def _extract_yaml(data, pointer):
        if isinstance(data, list):
            for index, item in enumerate(data):
                yield from _extract_yaml(item, pointer=f'{pointer}/{index}')
        elif isinstance(data, dict):
            for key, value in data.items():
                new_pointer = f'{pointer}/{key}'
                yield from _extract_yaml(value, pointer=new_pointer)
                text = text_to_translate(value, key in keys)
                if text:
                    yield 1, '', text, [new_pointer]

    yield from _extract_yaml(yaml.safe_load(fileobj.read().decode()), '')


def _get_option_as_list(options, key):
    if options:
        return options.get(key, '').split(',')
    return []
