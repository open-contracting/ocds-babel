"""
In the Sphinx build configuration file (``conf.py``), you can use :code:`translate` to translate codelist CSV files and JSON Schema files:

.. code:: python

    import os
    from glob import glob
    from pathlib import Path

    from ocds_babel.translate import translate


    def setup(app):
        basedir = Path(os.path.realpath(__file__)).parents[1]
        localedir = basedir / 'locale'
        language = app.config.overrides.get('language', 'en')
        headers = ['Title', 'Description', 'Extension']

        translate([
            (glob(str(basedir / 'schema' / '*-schema.json')), basedir / 'build' / language, 'schema'),
            (glob(str(basedir / 'schema' / 'codelists')), basedir / 'build' / language, 'codelists'),
        ], localedir, language, headers)

:code:`translate` automatically determines the translation method to used based on filenames. The arguments to :code:`translate` are:

#. A list of tuples. Each tuple has three values:

   #. Input files (a list of paths of files to translate)
   #. Output directory (the path of the directory in which to write translated files)
   #. Gettext domain (the filename without extension of the message catalog to use)

#. Locale directory (the path of the directory containing message catalog files)
#. Target language (the code of the language to translate to)
#. Optional keyword arguments to replace ``{{marker}}`` markers with values, e.g. :code:`version='1.1'`

Methods are also available for translating ``extension.json`` and for translating Markdown files.

Install requirements for Markdown translation
---------------------------------------------

To translate Markdown files, you must install Sphinx>=1.6 and (for now) forks of `CommonMark <https://commonmarkpy.readthedocs.io/en/latest/>`__ and `recommonmark <https://recommonmark.readthedocs.io/en/latest/>`__, until these bugs are fixed: `#225 <https://github.com/readthedocs/commonmark.py/pull/225>`__, `#181 <https://github.com/readthedocs/recommonmark/pull/181>`__, `#186 <https://github.com/readthedocs/recommonmark/pull/186>`__, `#187 <https://github.com/readthedocs/recommonmark/pull/187>`__.

Install a recent version of Sphinx with:

.. code-block:: bash

    pip install ocds-babel[markdown]

or install a specific version like:

.. code-block:: bash

    pip install 'Sphinx==2.2.1'

Then, install the forks of CommonMark and recommonmark:

.. code-block:: bash

    pip install -e git+https://github.com/readthedocs/commonmark.py.git@dafae75015cc342f3fddb499674bab97ac4a6a96#egg=commonmark -e git+https://github.com/jpmckinney/recommonmark.git@hotfix#egg=recommonmark
"""  # noqa: E501

import csv
import gettext
import json
import logging
import os
from copy import deepcopy
from io import StringIO

from ocds_babel import TRANSLATABLE_EXTENSION_METADATA_KEYWORDS, TRANSLATABLE_SCHEMA_KEYWORDS
from ocds_babel.util import text_to_translate

try:
    from ocds_babel.translate_markdown import translate_markdown
except ImportError:
    pass

logger = logging.getLogger('ocds_babel')


def translate(configuration, localedir, language, headers, **kwargs):
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
                else:
                    raise NotImplementedError(basename)
                w.write(method(r, translators[domain], **kwargs))


# This should roughly match the logic of `extract_codelist`.
def translate_codelist(io, translator, headers=[], **kwargs):
    """
    Accepts a CSV file as an IO object, and returns its translated contents in CSV format.
    """
    reader = csv.DictReader(io)

    fieldnames = [translator.gettext(fieldname) for fieldname in reader.fieldnames]
    rows = translate_codelist_data(reader, translator, headers, **kwargs)

    io = StringIO()
    writer = csv.DictWriter(io, fieldnames, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

    return io.getvalue()


def translate_codelist_data(source, translator, headers=[], **kwargs):
    """
    Accepts CSV rows as an iterable object (e.g. a list of dictionaries), and returns translated rows.
    """
    rows = []
    for row in source:
        data = {}
        for key, value in row.items():
            text = text_to_translate(value, key in headers)
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
    data = json.load(io)

    data = translate_schema_data(data, translator, **kwargs)

    return _json_dumps(data)


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
    data = json.load(io)

    data = translate_extension_metadata_data(data, translator, lang, **kwargs)

    return _json_dumps(data)


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


def _json_dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2, separators=(',', ': '))
