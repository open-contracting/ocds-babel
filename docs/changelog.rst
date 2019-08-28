Changelog
=========

0.1.0 (2019-05-23)
------------------

This version contains backwards-incompatible changes. These changes were made so that the package can be shared between the Open Contracting Data Standard (OCDS) and Beneficial Ownership Data Standard (BODS). You must now:

-  Specify the headers to translate and the files to ignore (if any) in configuration files that use the ``ocds_codelist`` entry point.
-  Specify the headers to translate in a ``headers`` argument to the ``translate`` method.
-  Separately install Sphinx 1.5.1 if you are translating Markdown-to-Markdown.

The readme instructions reflect these changes.

.. _section-1:

0.0.8 (2019-01-26)
------------------

-  Fix inline rendering in ``list-table`` ReStructuredText directives.

.. _section-2:

0.0.7 (2019-01-25)
------------------

-  Render inline elements in ``list-table`` ReStructuredText directives.

.. _section-3:

0.0.6 (2019-01-09)
------------------

-  Fix errors due to ``csv-table`` directive in ``translate_markdown_data``.

.. _section-4:

0.0.5 (2018-11-20)
------------------

-  Add ``translate_codelist_data``, ``translate_schema_data``, ``translate_extension_metadata_data``, ``translate_markdown_data``, which have parsed objects as input and output.

.. _section-5:

0.0.4 (2018-11-13)
------------------

-  Translate ``list-table`` ReStructuredText directives.

.. _section-6:

0.0.3 (2018-11-02)
------------------

-  Use universal newlines mode, to avoid CSV parsing errors.
-  Fix bug in parsing of Markdown code block.
-  Fix warning if CSV field name is empty.

.. _section-7:

0.0.2 (2018-10-31)
------------------

-  Fix bug if ``lang`` keyword argument is already specified.

.. _section-8:

0.0.1 (2018-10-31)
------------------

First release.
