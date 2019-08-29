Babel extractors
================

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

API
---

.. automodule:: ocds_babel.extract
   :members:
   :undoc-members:
