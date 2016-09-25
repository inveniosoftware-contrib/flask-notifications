..
    This file is part of Flask-Notifications
    Copyright (C) 2015 CERN.

    Flask-Notifications is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License; see LICENSE file for
    more details.

=====================
 Flask-Notifications
=====================

.. image:: https://img.shields.io/travis/inveniosoftware/flask-notifications.svg
:target: https://travis-ci.org/inveniosoftware/flask-notifications

.. image:: https://img.shields.io/coveralls/inveniosoftware/flask-notifications.svg
:target: https://coveralls.io/r/inveniosoftware/flask-notifications

.. image:: https://img.shields.io/github/tag/inveniosoftware/flask-notifications.svg
:target: https://github.com/inveniosoftware/flask-notifications/releases

.. image:: https://img.shields.io/pypi/dm/flask-notifications.svg
:target: https://pypi.python.org/pypi/flask-notifications

.. image:: https://img.shields.io/github/license/inveniosoftware/flask-notifications.svg
:target: https://github.com/inveniosoftware/flask-notifications/blob/master/LICENSE

About
=====

Flask-Notifications is a Flask extension that provides generic notification
framework.

Installation
============

Flask-Notifications is on PyPI so all you need is: ::

    pip install Flask-Notifications

Documentation
=============

Documentation is readable at http://flask-notifications.readthedocs.io or can
be build using Sphinx: ::

    git submodule init
    git submodule update
    pip install Sphinx
    python setup.py build_sphinx

Testing
=======

Running the test suite is as simple as: ::

    python setup.py test

or, to also show code coverage: ::

    ./run-tests.sh

