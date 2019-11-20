from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ocds-babel',
    version='0.1.0',
    author='Open Contracting Partnership',
    author_email='data@open-contracting.org',
    url='https://github.com/open-contracting/ocds-babel',
    description='Provides Babel extractors and translation methods for standards like OCDS or BODS',
    license='BSD',
    packages=find_packages(exclude=['tests', 'tests.*']),
    long_description=long_description,
    extras_require={
        'markdown': [
            'docutils',
            # See docs/api/translate.rst
            # 'recommonmark',
            'Sphinx>=1.6',
        ],
        'test': [
            'coveralls',
            'pytest',
            'pytest-cov',
        ],
        'docs': [
            'Sphinx',
            'sphinx-autobuild',
            'sphinx_rtd_theme',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'babel.extractors': [
            'ocds_codelist = ocds_babel.extract:extract_codelist',
            'ocds_schema = ocds_babel.extract:extract_schema',
        ],
    },
)
