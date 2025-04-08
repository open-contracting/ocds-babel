"""
In the Sphinx build configuration file (``conf.py``), ``translate`` codelist CSV files and JSON Schema files.

.. code:: python

    import os
    from glob import glob
    from pathlib import Path

    from ocds_babel.translate import translate


    def setup(app):
        basedir = Path(__file__).resolve().parents[1]
        localedir = basedir / 'locale'
        language = app.config.overrides.get('language', 'en')
        headers = ['Title', 'Description', 'Extension']

        translate([
            (glob(str(basedir / 'schema' / '*-schema.json')), basedir / 'build' / language, 'schema'),
            (glob(str(basedir / 'schema' / 'codelists')), basedir / 'build' / language, 'codelists'),
        ], localedir, language, headers)

:code:`translate` automatically determines the translation method to used based on filenames.
The arguments to :code:`translate` are:

#. A list of tuples. Each tuple has three values:

   #. Input files (a list of paths of files to translate)
   #. Output directory (the path of the directory in which to write translated files)
   #. Gettext domain (the filename without extension of the message catalog to use)

#. Locale directory (the path of the directory containing message catalog files)
#. Target language (the code of the language to translate to)
#. Optional keyword arguments to replace ``{{marker}}`` markers with values, e.g. :code:`version='1.1'`

Methods are also available for translating ``extension.json``, Markdown files and YAML files.

Install requirements for Markdown translation
---------------------------------------------

To translate Markdown files, you must install:

.. code-block:: bash

    pip install ocds-babel[markdown]
"""

import contextlib
import csv
import gettext
import json
import logging
import os
from copy import deepcopy
from io import StringIO

import yaml

from ocds_babel import TRANSLATABLE_EXTENSION_METADATA_KEYWORDS, TRANSLATABLE_SCHEMA_KEYWORDS
from ocds_babel.util import text_to_translate

with contextlib.suppress(ImportError):
    from ocds_babel.translate_markdown import translate_markdown, translate_markdown_data  # noqa: F401

logger = logging.getLogger('ocds_babel')


def translate(configuration, localedir, language, headers, keys, **kwargs):
    """
    Write files, translating any translatable strings.

    For translated strings in schema files, replace `{{lang}}` with the language code. Keyword arguments may specify
    additional replacements.
    """
    translators = {}

    for sources, target, domain in configuration:
        logger.info('Translating to %s using "%s" domain, into %s', language, domain, target)

        translators.setdefault(domain, gettext.translation(
            domain, localedir, languages=[language], fallback=language == 'en'))

        os.makedirs(target, exist_ok=True)

        for source in sources:
            basename = os.path.basename(source)
            with open(source) as r, open(os.path.join(target, basename), 'w') as w:
                if basename == 'extension.json':
                    method = translate_extension_metadata
                    kwargs.update(lang=language)
                elif source.endswith('.csv'):
                    method = translate_codelist
                    kwargs.update(headers=headers)
                elif source.endswith('.json'):
                    method = translate_schema
                    kwargs.update(lang=language)
                elif source.endswith('.md'):
                    method = translate_markdown
                elif source.endswith('.yaml'):
                    method = translate_yaml
                    kwargs.update(keys=keys)
                else:
                    raise NotImplementedError(basename)
                w.write(method(r, translators[domain], **kwargs))


# This should roughly match the logic of `extract_codelist`.
def translate_codelist(io, translator, headers=(), **kwargs):
    """Accept a CSV file as an IO object, and return its translated contents in CSV format."""
    reader = csv.DictReader(io)

    fieldnames = [translator.gettext(fieldname) for fieldname in reader.fieldnames]
    rows = translate_codelist_data(reader, translator, headers, **kwargs)

    io = StringIO()
    writer = csv.DictWriter(io, fieldnames, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

    return io.getvalue()


def translate_codelist_data(source, translator, headers=(), **kwargs):
    """Accept CSV rows as an iterable object (e.g. a list of dictionaries), and return translated rows."""
    rows = []
    for row in source:
        data = {}
        for key, value in row.items():
            text = text_to_translate(value, key in headers)
            data[translator.gettext(key)] = translator.gettext(text) if text else value
        rows.append(data)
    return rows


# This should roughly match the logic of `extract_schema`.
def translate_schema(io, translator, **kwargs):
    """Accept a JSON file as an IO object, and return its translated contents in JSON format."""
    data = json.load(io)

    data = translate_schema_data(data, translator, **kwargs)

    return _json_dumps(data)


def translate_schema_data(source, translator, **kwargs):
    """Accept JSON data, and return translated data."""
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
    """Accept an extension metadata file as an IO object, and return its translated contents in JSON format."""
    data = json.load(io)

    data = translate_extension_metadata_data(data, translator, lang, **kwargs)

    return _json_dumps(data)


def translate_extension_metadata_data(source, translator, lang='en', **kwargs):
    """Accept extension metadata, and return translated metadata."""
    data = deepcopy(source)

    for key in TRANSLATABLE_EXTENSION_METADATA_KEYWORDS:
        value = data.get(key)

        if isinstance(value, dict):
            value = value.get('en')

        text = text_to_translate(value)
        if text:
            data[key] = {lang: translator.gettext(text)}

    return data


# This should roughly match the logic of `extract_yaml`.
def translate_yaml(io, translator, keys=(), **kwargs):
    """Accept a YAML file as an IO object, and return its translated contents in YAML format."""
    data = yaml.safe_load(io)

    data = translate_yaml_data(data, translator, keys, **kwargs)

    return yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)


def translate_yaml_data(source, translator, keys=(), **kwargs):
    """Accept YAML data, and return translated data."""
    def _translate_yaml_data(data):
        if isinstance(data, list):
            for item in data:
                _translate_yaml_data(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                _translate_yaml_data(value)
                text = text_to_translate(value, key in keys)
                if text:
                    data[key] = translator.gettext(text)
                    for old, new in kwargs.items():
                        data[key] = data[key].replace('{{' + old + '}}', new)

    data = deepcopy(source)
    _translate_yaml_data(data)
    return data


def _json_dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2)
