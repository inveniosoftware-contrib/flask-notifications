# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

# Use Python-2.7:
FROM python:2.7

# Install some prerequisites ahead of `setup.py` in order to profit
# from the docker build cache:
RUN pip install 'coverage<4.0a1' \
                flask \
                pydocstyle \
                pytest \
                pytest-cov \
                pytest-pep8 \
                sphinx

# Add sources to `code` and work there:
WORKDIR /code
ADD . /code

# Install Flask-Notifications:
RUN pip install -e .[docs]

# Install extra dependencies for the consumers in Flask-Notifications
# e.g. installing flask-notifications[mail] will use -> flask-mail
# e.g. installing flask-notifications[email] will use -> flask-email
# Install both as our simple example use them
RUN pip install flask-mail flask-email requests

# Run container as user `flasknotifications` with UID `1000`, which should match
# current host user in most situations:
RUN adduser --uid 1000 --disabled-password --gecos '' flasknotifications && \
    chown -R flasknotifications:flasknotifications /code

# Start simple example application:
USER flasknotifications
CMD  ["python", "examples/simple/app.py"]
