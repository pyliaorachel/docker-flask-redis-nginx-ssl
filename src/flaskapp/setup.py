import sys

from setuptools import setup, find_packages


setup(
    version='0.1',
    name='exampleflask',
    package_dir={'': 'example'},
    packages=find_packages(where='example'),
    install_requires=[
        'flask',
        'gunicorn',
        'redis',
    ],
)
