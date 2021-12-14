from setuptools import find_packages, setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ocds-babel',
    version='0.3.5',
    author='Open Contracting Partnership',
    author_email='data@open-contracting.org',
    url='https://github.com/open-contracting/ocds-babel',
    description='Provides Babel extractors and translation methods for standards like OCDS or BODS',
    license='BSD',
    packages=find_packages(exclude=['tests', 'tests.*']),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    extras_require={
        'markdown': [
            'markdown-it-py>=2',
            'mdformat',
        ],
        'test': [
            'pytest',
        ],
        'docs': [
            'furo',
            'sphinx',
            'sphinx-autobuild',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    entry_points={
        'babel.extractors': [
            'ocds_codelist = ocds_babel.extract:extract_codelist',
            'ocds_schema = ocds_babel.extract:extract_schema',
        ],
    },
)
