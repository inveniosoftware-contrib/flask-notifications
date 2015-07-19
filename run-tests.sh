#!/bin/sh
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

pep257 flask_notifications && \
sphinx-build -qnNW docs docs/_build/html && \
python setup.py test
