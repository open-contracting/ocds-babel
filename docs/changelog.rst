Changelog
=========

0.3.7 (2025-05-18)
------------------

-  Add support for YAML files.
-  Drop support for Python 3.8.

0.3.6 (2024-09-07)
------------------

-  Drop support for Python 3.7.

0.3.5 (2021-12-14)
------------------

-  Upgrade to markdown-it-py 2.x.
-  Drop support for Python 3.6.

0.3.4 (2021-05-05)
------------------

-  Upgrade to markdown-it-py 1.x.

0.3.3 (2021-05-05)
------------------

-  Last release for markdown-it-py 0.x.

0.3.2 (2021-04-10)
------------------

-  Add Python wheels distribution.

0.3.1 (2021-02-16)
------------------

-  Set the Markdown level of translated content.

0.3.0 (2021-02-15)
------------------

-  Switch to mdformat from recommonmark.

   -  HTML blocks are not translated.
   -  Bullet lists use ``-`` bullets.
   -  Code spans use single backticks.

-  Drop support for Sphinx directives.

0.2.2 (2020-04-06)
------------------

-  Don't attempt to convert lists of links into ``toctree`` directives.

0.2.1 (2019-11-21)
------------------

-  Restore support for Sphinx 1.5 (and possibly earlier).

0.2.0 (2019-11-20)
------------------

-  Translate images and HTML.
-  Add support for Sphinx>=1.6 (requires forks of recommonmark and commonmark for now).
-  **Backwards-incompatible change:** Remove support for Sphinx<1.6 (restored in 0.2.1).

0.1.0 (2019-05-23)
------------------

This version contains backwards-incompatible changes. These changes were made so that the package can be shared between the Open Contracting Data Standard (OCDS) and Beneficial Ownership Data Standard (BODS). You must now:

-  Specify the headers to translate and the files to ignore (if any) in configuration files that use the ``ocds_codelist`` entry point.
-  Specify the headers to translate in a ``headers`` argument to the ``translate`` method.
-  Separately install Sphinx 1.5.1 if you are translating Markdown-to-Markdown.

The documentation reflects these changes.

0.0.8 (2019-01-26)
------------------

-  Fix inline rendering in ``list-table`` ReStructuredText directives.

0.0.7 (2019-01-25)
------------------

-  Render inline elements in ``list-table`` ReStructuredText directives.

0.0.6 (2019-01-09)
------------------

-  Fix errors due to ``csv-table`` directive in ``translate_markdown_data``.

0.0.5 (2018-11-20)
------------------

-  Add ``translate_codelist_data``, ``translate_schema_data``, ``translate_extension_metadata_data``, ``translate_markdown_data``, which have parsed objects as input and output.

0.0.4 (2018-11-13)
------------------

-  Translate ``list-table`` ReStructuredText directives.

0.0.3 (2018-11-02)
------------------

-  Use universal newlines mode, to avoid CSV parsing errors.
-  Fix bug in parsing of Markdown code block.
-  Fix warning if CSV field name is empty.

0.0.2 (2018-10-31)
------------------

-  Fix bug if ``lang`` keyword argument is already specified.

0.0.1 (2018-10-31)
------------------

First release.
