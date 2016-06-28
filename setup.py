# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

import os
import re
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

# Get the version string. Cannot be done with import!
with open(os.path.join('flask_notifications', 'version.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

tests_require = [
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest-runner>=2.7.0',
    'pytest>=2.8.0',
    'coverage>=4.0',
    'flask-email>=1.4.4',
    'flask-mail>=0.9.1',
    'pydocstyle>=1.0.0',
]

setup(
    name='Flask-Notifications',
    version=version,
    url='https://github.com/inveniosoftware/flask-notifications',
    license='BSD',
    author='CERN',
    author_email='info@inveniosoftware.org',
    description='Flask-Notifications is a Flask extension that adds support '
                'for real-time notifications.',
    long_description=open('README.rst').read(),
    packages=['flask_notifications'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'flask-celeryext',
        'redis',
        'gevent',
        'sse',
        'blinker',
        'jsonschema',
        'six'
    ],
    extras_require={
        'docs': ['sphinx'],
        'tests': tests_require,
        'flask-email': ['Flask-Email'],
        'flask-mail': ['Flask-Mail']
    },
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 4 - Beta'
    ],
)
