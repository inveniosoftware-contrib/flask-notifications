# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2015 CERN.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""A simple demo application showing Flask-Menu in action.

Usage:
  $ fig up
  $ firefox http://0.0.0.0:5000/
  $ firefox http://0.0.0.0:5000/first
  $ firefox http://0.0.0.0:5000/second
"""
import gevent
import gevent.monkey

from celery import Celery
from flask import Flask, render_template
from flask.json import dumps
from redis import StrictRedis
from flask.ext.notifications import NotificationService, Event
from flask.ext.notifications.event import ExtendedJSONEncoder

from gevent.pywsgi import WSGIServer
from sse import Sse
from flask.ext.notifications.ssenotifier import SseNotifier

gevent.monkey.patch_all()

app = Flask(__name__)

config = {
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": "587",
    "MAIL_USERNAME": "invnotifications@gmail.com",
    "MAIL_PASSWORD": "invenio888",
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "DEBUG": True,
    "CELERY_BROKER_URL": "redis://localhost:6379/0",
    "CELERY_RESULT_BACKEND": "redis://localhost:6379/0",
    "BROKER_TRANSPORT": "redis",
    "CELERY_ACCEPT_CONTENT": ["pickle", "json"],
    "REDIS_URL": "redis://localhost:6379/0"
}

app.config.update(config)
celery = Celery()

# Very important step, the celery must be configured if passed when initializing the NotificationService
celery.conf.update(config)

notifications = NotificationService(app=app, celery=celery)


@app.route('/')
def index():
    return render_template("sse.html")


@app.route('/notify')
def notify():
    """Send a notification"""
    event = Event("1", "This is a test", "This is the body of a test")
    json = dumps(event)
    print(json)
    event_from_parser = Event.from_json(json)

    assert event_from_parser.event_id == event.event_id
    assert event_from_parser.title == event.title
    assert event_from_parser.body == event.body
    notifications.notify(
        """{"body": "This is the body of a test", "event_id": "1", "title": "This is a test of a notification"}""")
    return "Sent event"


@app.route("/notifications")
def notifier():
    """Propagate and push notifications"""
    return notifications.notifier_response


if __name__ == '__main__':
    server = WSGIServer(("0.0.0.0", 8080), app)
    server.serve_forever()
