#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='isobar_ext',
    version='v0.5.1',
    description='A Python library to express and manipulate musical patterns extending original isobar library.',
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    author='Piotr Sakowski',
    author_email='piotereks@gmail.com',
    url='https://github.com/piotereks/isobar-ext',
    packages=find_packages(),
    install_requires=['python-osc', 'mido', 'python-rtmidi'],
    keywords=['sound', 'music', 'composition'],
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Artistic Software',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-timeout']
)
