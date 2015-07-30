# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""A simple_flaskmail demo application showing Flask-Notifications in action.

Usage:
  $ fig up
  $ firefox http://0.0.0.0:8080/
  $ firefox http://0.0.0.0:8080/notify_user
  $ firefox http://0.0.0.0:8080/notify_system
  $ firefox http://0.0.0.0:8080/notifications
"""
import os

import gevent
import gevent.monkey
from celery import Celery
from flask import Flask, render_template
from redis import StrictRedis
from gevent.pywsgi import WSGIServer
from flask.ext.notifications.consumers.email.flaskmail_consumer import \
    FlaskMailConsumer
from flask.ext.notifications.consumers.push.push_consumer import PushConsumer

from flask_notifications import Notifications, Event

gevent.monkey.patch_all()

app = Flask(__name__)

redis_url = os.environ['REDIS_URL']
redis_host = redis_url.split(":")[1][2:]

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
celery = Celery(__name__)

# Very important step, the celery must be configured
# if passed when initializing the NotificationService
celery.conf.update(config)

default_email_account = "invnotifications@gmail.com"
redis = StrictRedis(host=redis_host)

# Declaring our notifications extension
notifications = Notifications(app=app, celery=celery, redis=redis)

# Declaring the hubs for specific types of event
user_hub = notifications.hub_for("user")
system_hub = notifications.hub_for("system")


# Adding a new consumer to the user_hub
@user_hub.consumer()
def write_to_file(event, *args, **kwargs):
    f = open("events.log", "a+w")
    f.write(str(event))


push_consumer = PushConsumer(redis)
user_hub.consumers([PushConsumer])

mail_consumer = FlaskMailConsumer.from_app(
    app, default_email_account, [default_email_account]
)

# Registering one or more predefined consumers
system_hub.consumers([push_consumer, mail_consumer])


@app.route('/')
def index():
    return render_template("sse.html")


@app.route('/notify_user')
def notify_user_event():
    """Sends a notification of type user"""
    event = Event(1, "user", "This is a test", "This is the body of the test")
    notifications.notify(event.to_json())
    return "Sent event"


@app.route('/notify_system')
def notify_system_event():
    """Sends a notification of type system"""
    event = Event(1, "system", "This is a test", "This is the body of the test")
    notifications.notify(event.to_json())
    return "Sent event"


@app.route("/user_notifications")
def user_notifier():
    """Propagate and push notifications"""
    return notifications.create_push_notifier_for("user")


@app.route("/system_notification")
def system_notifier():
    """Propagate and push notifications"""
    return notifications.create_push_notifier_for("system")


if __name__ == '__main__':
    server = WSGIServer(("0.0.0.0", 8080), app)
    server.serve_forever()
