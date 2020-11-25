from setuptools import find_packages, setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ocds-babel',
    version='0.2.2',
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
            # See https://ocds-babel.readthedocs.io/en/latest/api/translate.html
            # 'recommonmark',
            'Sphinx>=1.5',
        ],
        'test': [
            'pytest',
        ],
        'docs': [
            'Sphinx',
            'sphinx-autobuild',
            'sphinx_rtd_theme',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'babel.extractors': [
            'ocds_codelist = ocds_babel.extract:extract_codelist',
            'ocds_schema = ocds_babel.extract:extract_schema',
        ],
    },
)
