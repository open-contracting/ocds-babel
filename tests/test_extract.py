import os
from tempfile import TemporaryDirectory

from ocds_babel.extract import extract_codelist, extract_extension_metadata, extract_schema, extract_yaml

options = {
    "headers": "Title,Description,Extension",
    "ignore": "currency.csv",
}

codelist = b"""Code,Title,Description,Extension,Category
  foo  ,  bar  ,  baz  ,  bzz  ,  zzz  
  bar  ,       ,  bzz  ,  zzz  ,  foo  
  baz  ,  bzz  ,       ,  foo  ,  bar  
  bzz  ,  zzz  ,  foo  ,       ,  baz  
"""  # noqa: W291


def assert_result(filename, content, method, options, expected):
    with TemporaryDirectory() as d:
        with open(os.path.join(d, filename), "wb") as f:
            f.write(content)

        with open(os.path.join(d, filename), "rb") as f:
            assert list(method(f, None, None, options)) == expected


def test_extract_codelist():
    assert_result(
        "test.csv",
        codelist,
        extract_codelist,
        options,
        [
            (0, "", "Code", ""),
            (0, "", "Title", ""),
            (0, "", "Description", ""),
            (0, "", "Extension", ""),
            (0, "", "Category", ""),
            (1, "", "bar", ["Title"]),
            (1, "", "baz", ["Description"]),
            (1, "", "bzz", ["Extension"]),
            (2, "", "bzz", ["Description"]),
            (2, "", "zzz", ["Extension"]),
            (3, "", "bzz", ["Title"]),
            (3, "", "foo", ["Extension"]),
            (4, "", "zzz", ["Title"]),
            (4, "", "foo", ["Description"]),
        ],
    )


def test_extract_codelist_currency():
    assert_result(
        "currency.csv",
        codelist,
        extract_codelist,
        options,
        [
            (0, "", "Code", ""),
            (0, "", "Title", ""),
            (0, "", "Description", ""),
            (0, "", "Extension", ""),
            (0, "", "Category", ""),
        ],
    )


def test_extract_codelist_fieldname():
    assert_result(
        "test.csv",
        b"Code,",
        extract_codelist,
        options,
        [
            (0, "", "Code", ""),
        ],
    )


def test_extract_codelist_newline():
    assert_result(
        "test.csv",
        b"Code\rfoo",
        extract_codelist,
        options,
        [
            (0, "", "Code", ""),
        ],
    )


def test_extract_schema():
    schema = b"""{
        "title": {
            "oneOf": [{
                "title": "  foo  ",
                "description": "  bar  "
            }, {
                "title": "  baz  ",
                "description": "  bzz  "
            }]
        },
        "description": {
            "title": "  zzz  ",
            "description": "    "
        }
    }"""

    assert_result(
        "schema.json",
        schema,
        extract_schema,
        None,
        [
            (1, "", "foo", ["/title/oneOf/0/title"]),
            (1, "", "bar", ["/title/oneOf/0/description"]),
            (1, "", "baz", ["/title/oneOf/1/title"]),
            (1, "", "bzz", ["/title/oneOf/1/description"]),
            (1, "", "zzz", ["/description/title"]),
        ],
    )


def test_extract_extension_metadata():
    metadata = b"""{
        "name": "  foo  ",
        "description": "  bar  "
    }"""

    assert_result(
        "extension.json",
        metadata,
        extract_extension_metadata,
        None,
        [
            (1, "", "foo", ["/name"]),
            (1, "", "bar", ["/description"]),
        ],
    )


def test_extract_extension_metadata_language_map():
    metadata_language_map = b"""{
        "name": {
            "en": "  foo  "
        },
        "description": {
            "en": "  bar  "
        }
    }"""

    assert_result(
        "extension.json",
        metadata_language_map,
        extract_extension_metadata,
        None,
        [
            (1, "", "foo", ["/name/en"]),
            (1, "", "bar", ["/description/en"]),
        ],
    )


def test_extract_extension_metadata_empty():
    assert_result("extension.json", b"{}", extract_extension_metadata, None, [])


def test_extract_yaml_list():
    yaml_list = b"""
    -   id: '1'
        title: foo
    -   id: '1'
        mapping: bar
    """

    assert_result(
        "test.yaml",
        yaml_list,
        extract_yaml,
        {"keys": "title,mapping"},
        [
            (1, "", "foo", ["/0/title"]),
            (1, "", "bar", ["/1/mapping"]),
        ],
    )


def test_extract_yaml_obj():
    yaml_obj = b"""
    foo: bar
    baz: bzz
    """

    assert_result(
        "test.yaml",
        yaml_obj,
        extract_yaml,
        {"keys": "foo,baz"},
        [
            (1, "", "bar", ["/foo"]),
            (1, "", "bzz", ["/baz"]),
        ],
    )
