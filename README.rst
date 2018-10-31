|PyPI version| |Build Status| |Dependency Status| |Coverage Status|

This Python package provides `Babel extractors <http://babel.pocoo.org/en/latest/messages.html>`__ and translation methods for OCDS documentation.

Examples
--------

Babel extractors
~~~~~~~~~~~~~~~~

Babel extractors can be specified in configuration files. For example::

    [ocds_codelist: schema/*/codelists/*.csv]

in ``babel_ocds_codelist.cfg``, or::

    [ocds_schema: schema/*/*-schema.json]

in ``babel_ocds_schema.cfg``.

Translation methods
~~~~~~~~~~~~~~~~~~~

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

        translate([
            ([], basedir / 'build' / language, 'schema'),
            ([], basedir / 'build' / language, 'codelists'),
        ], localedir, language)

The arguments to :code:`translate` are:

#. A list of tuples. Each tuple has three values:

   #. Input files (a list of paths of files to translate)
   #. Output directory (the path of the directory in which to write translated files)
   #. Gettext domain (the filename without extension of the message catalog to use)

#. Locale directory (the path of the directory containing message catalog files)
#. Target language (the code of the language to translate to)
#. Optional keyword arguments to replace ``{{marker}}`` markers with values, e.g. :code:`version='1.1'`.

:code:`translate` automatically determines the translation method to used based on filenames.

Methods are also available for translating ``extension.json`` and for translating Markdown-to-Markdown.

.. |PyPI version| image:: https://badge.fury.io/py/ocds-babel.svg
   :target: https://badge.fury.io/py/ocds-babel
.. |Build Status| image:: https://secure.travis-ci.org/open-contracting/ocds-babel.png
   :target: https://travis-ci.org/open-contracting/ocds-babel
.. |Dependency Status| image:: https://requires.io/github/open-contracting/ocds-babel/requirements.svg
   :target: https://requires.io/github/open-contracting/ocds-babel/requirements/
.. |Coverage Status| image:: https://coveralls.io/repos/github/open-contracting/ocds-babel/badge.png?branch=master
   :target: https://coveralls.io/github/open-contracting/ocds-babel?branch=master
