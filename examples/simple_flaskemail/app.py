# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""A simple_flaskemail demo application showing Flask-Notifications in action.

Usage:
  $ fig up
  $ firefox http://0.0.0.0:5000/
  $ firefox http://0.0.0.0:5000/first
  $ firefox http://0.0.0.0:5000/second
"""
import os

import gevent
import gevent.monkey
from celery import Celery
from flask import Flask, render_template
from redis import StrictRedis
from gevent.pywsgi import WSGIServer

from flask_notifications import NotificationService
from flask_notifications.consumers.email.flaskemail import FlaskEmailDependency
from flask_notifications.event import ExtendedJSONEncoder

gevent.monkey.patch_all()

app = Flask(__name__)

redis_url = os.environ['REDIS_URL']
config = {
    # Email configuration for Flask-Email
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_PORT": "587",
    "EMAIL_HOST_USER": "invnotifications@gmail.com",
    "EMAIL_HOST_PASSWORD": os.environ["INVENIO_GMAIL_PASSWORD"],
    "EMAIL_USE_TLS": True,
    "EMAIL_USE_SSL": False,
    "EMAIL_BACKEND": "flask.ext.email.backends.smtp.Mail",

    "DEBUG": True,
    "CELERY_BROKER_URL": redis_url,
    "CELERY_RESULT_BACKEND": redis_url,
    "BROKER_TRANSPORT": "redis",
    "BROKER_URL": redis_url,
    "CELERY_ACCEPT_CONTENT": ["pickle", "json"],
    "REDIS_URL": redis_url
}

app.config.update(config)
celery = Celery()

# Very important step, the celery must be configured if passed when initializing the NotificationService
celery.conf.update(config)

default_email_account = "invnotifications@gmail.com"
flaskemail = FlaskEmailDependency.from_app(app, default_email_account, [default_email_account])
redis = StrictRedis(host="redis")
notifications = NotificationService(app=app, celery=celery, redis=redis, email_dependency=flaskemail)


@app.route('/')
def index():
    return render_template("sse.html")


@app.route('/notify')
def notify():
    """Sends a notification"""
    notifications.notify_all(
        """{"body": "This is the body of a test", "event_id": "1", "title": "This is a test of a notification"}""")
    return "Sent event"


@app.route("/notifications")
def notifier():
    """Propagate and push notifications"""
    return notifications.create_push_notifier()


if __name__ == '__main__':
    server = WSGIServer(("0.0.0.0", 8081), app)
    server.serve_forever()
