from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ocds-babel',
    version='0.0.1',
    author='Open Contracting Partnership',
    author_email='data@open-contracting.org',
    url='https://github.com/open-contracting/ocds-babel',
    description='',
    license='BSD',
    packages=find_packages(),
    long_description=long_description,
    install_requires=[
        'babel',
    ],
    extras_require={
        'test': [
            'coveralls',
            'pytest',
            'pytest-cov',
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
