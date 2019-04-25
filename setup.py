"""The setup script."""
from setuptools import setup, find_packages
from os.path import exists

from intake_dcat._version import __version__ as version

readme = open("README.md").read() if exists("README.md") else ""


setup(
    name='intake-dcat',
    description='DCAT to Intake Catalog translation layer',
    long_description=readme,
    long_description_content_type='text/markdown',
    maintainer='Ian Rose',
    maintainer_email='ian.rose@lacity.org',
    url='https://github.com/CityOfLosAngeles/intake-dcat',
    packages=find_packages(),
    package_dir={'intake-dcat': 'intake-dcat'},
    include_package_data=True,
    install_requires=[
        'geopandas>=0.5',
        'intake>=0.4.4',
        'intake-geopandas>=0.2.2',
        'pyyaml>=5',
        'requests',
        's3fs',
    ],
    entry_points={
        'console_scripts': [
            'intake-dcat = intake_dcat.cli:main'
        ]
    },
    license='Apache-2.0 license',
    zip_safe=False,
    keywords='intake dcat',
    version=version,
)
