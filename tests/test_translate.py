import csv
import gettext
import json
import logging
import os
from glob import glob
from tempfile import TemporaryDirectory

from ocds_babel.translate import translate

headers = ['Title', 'Description', 'Extension']

codelist = """Code,Title,Description
open,  Open  ,  All interested suppliers may submit a tender.  
selective,  Selective  ,  Only qualified suppliers are invited to submit a tender.  
"""  # noqa: W291

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

extension_readme = """##### Skip Heading

# Heading 1

## Heading 2

### Heading **3**

Paragraph text and ```literal text```

`Literal text`

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

<h3>Subheading</h3>

![Caption](http://example.com/example.png)

This is a [pending](examples/test.md) xref.

This is a **[bold link](http://example.com/test.md)**.

This is <em>inline HTML</em>.

* Bulleted list item 1
* Bulleted list item 2

1. Enumerated list item 1
2. Enumerated list item 2

```{eval-rst}
.. list-table::
    :header-rows: 1

    * - Before *Header 1* After
      - Before **Header 2** After
    * - Before ``Code`` After
      - Before `Link <http://example.com>`__ After
```

* [Link list item 1](http://example.com/en/1.html)
* [Link list item 2](http://example.com/en/2.html)
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
                'All interested suppliers may submit a tender.': 'Todos los proveedores interesados pueden enviar una propuesta.',  # noqa: E501
                'Only qualified suppliers are invited to submit a tender.': 'Sólo los proveedores calificados son invitados a enviar una propuesta.',  # noqa: E501
            }[args[0]]

    monkeypatch.setattr(gettext, 'translation', Translation)

    caplog.set_level(logging.INFO)

    with TemporaryDirectory() as sourcedir:
        with open(os.path.join(sourcedir, 'method.csv'), 'w') as f:
            f.write(codelist)

        with TemporaryDirectory() as builddir:
            translate([
                (glob(os.path.join(sourcedir, '*.csv')), builddir, 'codelists'),
            ], '', 'es', headers)

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
                'Schema for an Open Contracting Record package {{version}} [{{lang}}]': 'Esquema para un paquete de Registros de Contrataciones Abiertas {{version}} [{{lang}}]',  # noqa: E501
                'The record package contains a list of records along with some publishing…':  'El paquete de registros contiene una lista de registros junto con algunos…',  # noqa: E501
                'Releases': 'Entregas',
                'An array of linking identifiers or releases': 'Una matriz de enlaces a identificadores o entregas',
                'Linked releases': 'Entregas vinculadas',
                'A list of objects that identify the releases associated with this Open…':  'Una lista de objetos que identifican las entregas asociadas con este Open…',  # noqa: E501
                'Embedded releases': 'Entregas embebidas',
                'A list of releases, with all the data. The releases MUST be sorted into date…':  'Una lista de entregas, con todos los datos. Las entregas DEBEN ordenarse…',  # noqa: E501
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
            ], '', 'es', headers, version='1.1')

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
                    'Communicates the location of proposed or executed contract delivery.': 'Comunica la ubicación de la entrega del contrato propuesto o ejecutado.',  # noqa: E501
                }[args[0]]

        monkeypatch.setattr(gettext, 'translation', Translation)

        caplog.set_level(logging.INFO)

        with TemporaryDirectory() as sourcedir:
            with open(os.path.join(sourcedir, 'extension.json'), 'w') as f:
                f.write(metadata)

            with TemporaryDirectory() as builddir:
                translate([
                    ([os.path.join(sourcedir, 'extension.json')], builddir, 'schema'),
                ], '', 'es', headers)

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
                'Skip Heading': 'Entête à sauter',
                'Heading 1': 'Titre 1',
                'Heading 2': 'Titre 2',
                'Heading **3**': 'Titre **3**',
                'Paragraph text and ```literal text```': 'Texte de paragraphe et ```texte littéral```',
                '`Literal text`': '`Texte littéral`',
                'Blockquote text': 'Texte de citation',
                '![Caption](http://example.com/example.png)': '![Légende](http://example.com/example-fr.png)',
                'This is a [pending](examples/test.md) xref.': 'Ceci est un xref [en suspens](examples/test.md).',
                'This is a **[bold link](http://example.com/test.md)**.': 'Ceci est un **[lien en gras](http://example.com/test.md)**.',  # noqa: E501
                'This is <em>inline HTML</em>.': 'Ceci est <em>HTML en ligne</em>.',
                '<h3>Subheading</h3>': '<h3>Sous-titre</h3>',
                'Bulleted list item 1': 'Élément de liste à puces 1',
                'Bulleted list item 2': 'Élément de liste à puces 2',
                'Enumerated list item 1': 'Élément de liste énumérée 1',
                'Enumerated list item 2': 'Élément de liste énumérée 2',
                'Before *Header 1* After': 'Avant *En-tête 1* Après',
                'Before **Header 2** After': 'Avant **En-tête 2** Après',
                'Before ``Code`` After': 'Avant ``Code`` Après',
                'Before `Link <http://example.com>`__ After': 'Avant `Lien <http://example.com>`__ Après',
                '[Link list item 1](http://example.com/en/1.html)': '[Élément de liste de liens 1](http://example.com/fr/1.html)',  # noqa: E501
                '[Link list item 2](http://example.com/en/2.html)': '[Élément de liste de liens 2](http://example.com/fr/2.html)',  # noqa: E501
                # docutils ... optparse
                '%prog [options]': '%prog [options]',
                '': '',
            }[args[0]]

    monkeypatch.setattr(gettext, 'translation', Translation)

    caplog.set_level(logging.INFO)

    with TemporaryDirectory() as sourcedir:
        with open(os.path.join(sourcedir, 'README.md'), 'w') as f:
            f.write(extension_readme)

        with TemporaryDirectory() as builddir:
            translate([
                ([os.path.join(sourcedir, 'README.md')], builddir, 'docs'),
            ], '', 'fr', headers)

            with open(os.path.join(builddir, 'README.md')) as f:
                text = f.read()

    assert text == """# Entête à sauter

# Titre 1

## Titre 2

### Titre **3**

Texte de paragraphe et ```texte littéral```

`Texte littéral`

> Texte de citation

```none
Raw paragraph text
```

```default
Literal block
```

```json
{
    "json": "block"
}
```

<h3>Sous-titre</h3>

![Légende](http://example.com/example-fr.png)

Ceci est un xref [en suspens](examples/test.md).

Ceci est un **[lien en gras](http://example.com/test.md)**.

Ceci est <em>HTML en ligne</em>.

* Élément de liste à puces 1
* Élément de liste à puces 2

1. Élément de liste énumérée 1
1. Élément de liste énumérée 2

<table border="1" class="docutils">
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<thead valign="bottom">
<tr class="row-odd">
<th class="head">Avant <em>En-tête 1</em> Après</th>
<th class="head">Avant <strong>En-tête 2</strong> Après</th>
</tr>
</thead>
<tbody valign="top">
<tr class="row-even">
<td>Avant <tt class="docutils literal">Code</tt> Après</td>
<td>Avant <a class="reference external" href="http://example.com">Lien</a> Après</td>
</tr>
</tbody>
</table>

* [Élément de liste de liens 1](http://example.com/fr/1.html)
* [Élément de liste de liens 2](http://example.com/fr/2.html)
"""

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == 'Translating to fr using "docs" domain, into {}'.format(builddir)
