Translation methods
===================

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

To translate Markdown files, you must install Sphinx>=1.6 and (for now) forks of [CommonMark](https://commonmarkpy.readthedocs.io/en/latest/) and [recommonmark](https://recommonmark.readthedocs.io/en/latest/).

Install a recent version of Sphinx with::

    pip install ocds-babel[markdown]

or install a specific version like::

    pip install 'Sphinx==2.2.1'

Then, install the forks of CommonMark and recommonmark::

    pip install -e git+https://github.com/jpmckinney/commonmark.git@hotfix#egg=commonmark -e git+https://github.com/jpmckinney/recommonmark.git@hotfix#egg=recommonmark

API
---

.. automodule:: ocds_babel.translate
   :members:
   :undoc-members:
