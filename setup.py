#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='isobar',
    version='0.1.1',
    description='A Python library to express and manipulate musical patterns',
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    author='Daniel Jones',
    author_email='dan-isobar@erase.net',
    url='https://github.com/ideoforms/isobar',
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
