import csv
import gettext
import json
import logging
import os
from glob import glob
from tempfile import TemporaryDirectory

from ocds_babel.translate import translate

codelist = """Code,Title,Description
open,  Open  ,  All interested suppliers may submit a tender.  
selective,  Selective  ,  Only qualified suppliers are invited to submit a tender.  
"""  # noqa

schema = """{
  "title": "Schema for an Open Contracting Record package {{version}} [{{lang}}]",
  "description": "The record package contains a list of records along with some publishing…",
  "definitions": {
    "record": {
      "properties": {
        "releases": {
          "title": "Releases",
          "description": "An array of linking identifiers or releases",
          "oneOf": [
            {
              "title": "  Linked releases  ",
              "description": "  A list of objects that identify the releases associated with this Open…  "
            },
            {
              "title": "  Embedded releases  ",
              "description": "  A list of releases, with all the data. The releases MUST be sorted into date…  "
            }
          ]
        }
      }
    }
  }
}"""

extension_metadata = """{
  "name": "  Location  ",
  "description": "  Communicates the location of proposed or executed contract delivery.  ",
  "compatibility": [
    "1.1"
  ]
}"""

extension_metadata_language_map = """{
  "name": {
    "en": "  Location  "
  },
  "description": {
    "en": "  Communicates the location of proposed or executed contract delivery.  "
  },
  "compatibility": [
    "1.1"
  ]
}"""

extension_readme = """# Heading 1

## Heading 2

Paragraph text

> Blockquote text

    Raw paragraph text

```
Literal block
```

```json
{
    "json": "block"
}
```

```eval_rst
.. extensiontable::
   :extension: location
```

* Bulleted list item 1
* Bulleted list item 2

1. Enumerated list item 1
2. Enumerated list item 1
"""


def test_translate_codelists(monkeypatch, caplog):
    class Translation(object):
        def __init__(self, *args, **kwargs):
            pass

        def gettext(self, *args, **kwargs):
            return {
                'Code': 'Código',
                'Title': 'Título',
                'Description': 'Descripción',
                'Open': 'Abierta',
                'Selective': 'Selectiva',
                'All interested suppliers may submit a tender.': 'Todos los proveedores interesados pueden enviar una propuesta.',  # noqa
                'Only qualified suppliers are invited to submit a tender.': 'Sólo los proveedores calificados son invitados a enviar una propuesta.',  # noqa
            }[args[0]]

    monkeypatch.setattr(gettext, 'translation', Translation)

    caplog.set_level(logging.INFO)

    with TemporaryDirectory() as sourcedir:
        with open(os.path.join(sourcedir, 'method.csv'), 'w') as f:
            f.write(codelist)

        with TemporaryDirectory() as builddir:
            translate([
                (glob(os.path.join(sourcedir, '*.csv')), builddir, 'codelists'),
            ], '', 'es')

            with open(os.path.join(builddir, 'method.csv')) as f:
                rows = [dict(row) for row in csv.DictReader(f)]

    assert rows == [{
        'Código': 'open',
        'Descripción': 'Todos los proveedores interesados pueden enviar una propuesta.',
        'Título': 'Abierta'
    }, {
        'Código': 'selective',
        'Descripción': 'Sólo los proveedores calificados son invitados a enviar una propuesta.',
        'Título': 'Selectiva'
    }]

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == 'Translating to es using "codelists" domain, into {}'.format(builddir)


def test_translate_schema(monkeypatch, caplog):
    class Translation(object):
        def __init__(self, *args, **kwargs):
            pass

        def gettext(self, *args, **kwargs):
            return {
                'Schema for an Open Contracting Record package {{version}} [{{lang}}]': 'Esquema para un paquete de Registros de Contrataciones Abiertas {{version}} [{{lang}}]',  # noqa
                'The record package contains a list of records along with some publishing…':  'El paquete de registros contiene una lista de registros junto con algunos…',  # noqa
                'Releases': 'Entregas',
                'An array of linking identifiers or releases': 'Una matriz de enlaces a identificadores o entregas',
                'Linked releases': 'Entregas vinculadas',
                'A list of objects that identify the releases associated with this Open…':  'Una lista de objetos que identifican las entregas asociadas con este Open…',  # noqa
                'Embedded releases': 'Entregas embebidas',
                'A list of releases, with all the data. The releases MUST be sorted into date…':  'Una lista de entregas, con todos los datos. Las entregas DEBEN ordenarse…',  # noqa
            }[args[0]]

    monkeypatch.setattr(gettext, 'translation', Translation)

    caplog.set_level(logging.INFO)

    with TemporaryDirectory() as sourcedir:
        with open(os.path.join(sourcedir, 'record-package-schema.json'), 'w') as f:
            f.write(schema)

        with open(os.path.join(sourcedir, 'untranslated.json'), 'w') as f:
            f.write(schema)

        with TemporaryDirectory() as builddir:
            translate([
                ([os.path.join(sourcedir, 'record-package-schema.json')], builddir, 'schema'),
            ], '', 'es', version='1.1')

            with open(os.path.join(builddir, 'record-package-schema.json')) as f:
                data = json.load(f)

            assert not os.path.exists(os.path.join(builddir, 'untranslated.json'))

    assert data == {
      "title": "Esquema para un paquete de Registros de Contrataciones Abiertas 1.1 [es]",
      "description": "El paquete de registros contiene una lista de registros junto con algunos…",
      "definitions": {
        "record": {
          "properties": {
            "releases": {
              "title": "Entregas",
              "description": "Una matriz de enlaces a identificadores o entregas",
              "oneOf": [
                {
                  "title": "Entregas vinculadas",
                  "description": "Una lista de objetos que identifican las entregas asociadas con este Open…"
                },
                {
                  "title": "Entregas embebidas",
                  "description": "Una lista de entregas, con todos los datos. Las entregas DEBEN ordenarse…"
                }
              ]
            }
          }
        }
      }
    }

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == 'Translating to es using "schema" domain, into {}'.format(builddir)


def test_translate_extension_metadata(monkeypatch, caplog):
    for metadata in (extension_metadata, extension_metadata_language_map):
        class Translation(object):
            def __init__(self, *args, **kwargs):
                pass

            def gettext(self, *args, **kwargs):
                return {
                    'Location': 'Ubicación',
                    'Communicates the location of proposed or executed contract delivery.': 'Comunica la ubicación de la entrega del contrato propuesto o ejecutado.',  # noqa
                }[args[0]]

        monkeypatch.setattr(gettext, 'translation', Translation)

        caplog.set_level(logging.INFO)

        with TemporaryDirectory() as sourcedir:
            with open(os.path.join(sourcedir, 'extension.json'), 'w') as f:
                f.write(metadata)

            with TemporaryDirectory() as builddir:
                translate([
                    ([os.path.join(sourcedir, 'extension.json')], builddir, 'schema'),
                ], '', 'es')

                with open(os.path.join(builddir, 'extension.json')) as f:
                    data = json.load(f)

        assert data == {
            "name": {
                "es": "Ubicación"
            },
            "description": {
                "es": "Comunica la ubicación de la entrega del contrato propuesto o ejecutado."
            },
            "compatibility": [
                "1.1"
            ]
        }

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'INFO'
        assert caplog.records[0].message == 'Translating to es using "schema" domain, into {}'.format(builddir)

        caplog.clear()


def test_translate_markdown(monkeypatch, caplog):
    class Translation(object):
        def __init__(self, *args, **kwargs):
            pass

        def gettext(self, *args, **kwargs):
            return {
                'Heading 1': 'Titre 1',
                'Heading 2': 'Titre 2',
                'Paragraph text': 'Texte de paragraphe',
                'Blockquote text': 'Texte de citation',
                'Raw paragraph text': 'Texte de paragraphe brut',
                'Literal block': 'Bloc littéral',
                'Bulleted list item 1': 'Élément de liste à puces 1',
                'Bulleted list item 2': 'Élément de liste à puces 2',
                'Enumerated list item 1': 'Élément de liste énumérée 1',
                'Enumerated list item 2': 'Élément de liste énumérée 2',
                # docutils ... optparse
                '%prog [options]': '%prog [options]',
            }[args[0]]

    monkeypatch.setattr(gettext, 'translation', Translation)

    caplog.set_level(logging.INFO)

    with TemporaryDirectory() as sourcedir:
        with open(os.path.join(sourcedir, 'README.md'), 'w') as f:
            f.write(extension_readme)

        with TemporaryDirectory() as builddir:
            translate([
                ([os.path.join(sourcedir, 'README.md')], builddir, 'docs'),
            ], '', 'fr')

            with open(os.path.join(builddir, 'README.md')) as f:
                text = f.read()

    assert text == """# Titre 1

## Titre 2

Texte de paragraphe

> Texte de citation

    Texte de paragraphe brut

```
Bloc littéral
```

```json
{
    "json": "block"
}
```

```eval_rst
.. extensiontable::
   :extension: location
```

* Élément de liste à puces 1
* Élément de liste à puces 2

1. Élément de liste énumérée 1
2. Élément de liste énumérée 2
"""

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == 'Translating to es using "docs" domain, into {}'.format(builddir)
