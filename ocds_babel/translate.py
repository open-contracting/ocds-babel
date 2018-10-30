import csv
import gettext
import glob
import json
import logging
import os
from collections import OrderedDict

from ocds_babel import TRANSLATABLE_CODELIST_HEADERS, TRANSLATABLE_SCHEMA_KEYWORDS

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
            fieldnames, rows = translate_codelist(r, translator)

            writer = csv.DictWriter(w, fieldnames, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)


# This should roughly match the logic of `extract_codelist`.
def translate_codelist(io, translator):
    reader = csv.DictReader(io)

    fieldnames = [translator.gettext(fieldname) for fieldname in reader.fieldnames]

    rows = []
    for row in reader:
        new = {}
        for key, value in row.items():
            if key in TRANSLATABLE_CODELIST_HEADERS and isinstance(value, str):
                value = value.strip()
                if value:
                    value = translator.gettext(value)
            new[translator.gettext(key)] = value
        rows.append(new)

    return fieldnames, rows


def translate_schemas(domain, filenames, sourcedir, builddir, localedir, language, ocds_version):
    """
    Writes files, translating the "title" and "description" values of JSON Schema files.

    These files are typically referenced by `jsonschema` directives.

    Args:

    *  domain: The gettext domain.
    *  filenames: A list of JSON Schema filenames to translate.
    *  sourcedir: The path to the directory containing the JSON Schema files.
    *  builddir: The path to the build directory.
    *  localedir: The path to the `locale` directory.
    *  language: A two-letter lowercase ISO369-1 code or BCP47 language tag.
    *  ocds_version: The minor version of OCDS to substitute into URL patterns.
    """
    logger.info('Translating schemas to {} using "{}" domain, from {} to {}'.format(
        language, domain, sourcedir, builddir))

    translator = translations_instance(domain, localedir, language)

    for name in filenames:
        os.makedirs(os.path.dirname(os.path.join(builddir, name)), exist_ok=True)

        with open(os.path.join(sourcedir, name)) as r, open(os.path.join(builddir, name), 'w') as w:
            data = translate_schema(r, translator, ocds_version, language)

            json.dump(data, w, indent=2, separators=(',', ': '), ensure_ascii=False)


# This should roughly match the logic of `extract_schema`.
def translate_schema(io, translator, ocds_version, language):
    def _translate_schema(data):
        if isinstance(data, list):
            for item in data:
                _translate_schema(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                if key in TRANSLATABLE_SCHEMA_KEYWORDS and isinstance(value, str):
                    value = value.strip()
                    if value:
                        data[key] = translator.gettext(value).replace('{{version}}', ocds_version).replace('{{lang}}', language)  # noqa: E501
                _translate_schema(value)

    data = json.load(io, object_pairs_hook=OrderedDict)

    _translate_schema(data)

    return data
