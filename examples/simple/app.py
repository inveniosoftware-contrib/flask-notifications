# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""A simple demo application showing Flask-Notifications in action.

Usage:
  $ fig up
  $ firefox http://0.0.0.0:8080/
  $ firefox http://0.0.0.0:8080/notify_user
  $ firefox http://0.0.0.0:8080/notify_system
"""
import os

import gevent
import gevent.monkey
from datetime import datetime
from celery import Celery
from flask import Flask, render_template
from redis import StrictRedis
from gevent.pywsgi import WSGIServer

from flask_notifications import Notifications, Event
from flask_notifications.consumers.push.push_consumer import PushConsumer
from flask_notifications.consumers.email.flaskmail_consumer import \
    FlaskMailConsumer
from flask_notifications.consumers.email.flaskemail_consumer import \
    FlaskEmailConsumer
from flask_notifications.filters.before_date import BeforeDate
from flask_notifications.filters.with_sender import WithSender
from flask_notifications.filters.with_receivers import WithReceivers
from flask_notifications.filters.with_event_type import WithEventType
from flask_notifications.filters.not_filter import Not

gevent.monkey.patch_all()

app = Flask(__name__)

# Get env variable and extract host from it
redis_url = os.environ["REDIS_URL"]
redis_host = redis_url.split(":")[1][2:]

default_email_account = "invnotifications@gmail.com"

config = {
    # Email configuration for Flask-Mail
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": "587",
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": default_email_account,
    "MAIL_PASSWORD": os.environ["INVENIO_GMAIL_PASSWORD"],

    # Email configuration for Flask-Email
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_PORT": "587",
    "EMAIL_HOST_USER": default_email_account,
    "EMAIL_HOST_PASSWORD": os.environ["INVENIO_GMAIL_PASSWORD"],
    "EMAIL_USE_TLS": True,
    "EMAIL_USE_SSL": False,

    "DEBUG": True,
    "CELERY_BROKER_URL": redis_url,
    "CELERY_RESULT_BACKEND": redis_url,
    "BROKER_TRANSPORT": "redis",
    "BROKER_URL": redis_url,
    "CELERY_ACCEPT_CONTENT": ["pickle", "json"],
    "REDIS_URL": redis_url,
}

app.config.update(config)
celery = Celery(__name__)

# Important step: Celery must be configured when passed
# to the Notifications extension
celery.conf.update(config)

redis = StrictRedis(host=redis_host)

# Define our notifications extension
notifications = Notifications(app=app, celery=celery, redis=redis)

# Define the hubs for specific types of event
user_hub = notifications.create_hub()
system_hub = notifications.create_hub()
user_hub_id = user_hub.hub_id
system_hub_id = system_hub.hub_id


# Add a new consumer to the user_hub
@user_hub.consumer(celery_task_name="app.write_to_file")
def write_to_file(event, *args, **kwargs):
    with open("events.log", "a+w") as f:
        f.write(str(event))


# Register manually a push consumer
push_consumer = PushConsumer(redis, user_hub_id)
user_hub.register_consumer(push_consumer)

# Create two independent email consumers
mail_consumer = FlaskMailConsumer.from_app(
    app, default_email_account, [default_email_account]
)

email_consumer = FlaskEmailConsumer.from_app(
    app, default_email_account, [default_email_account]
)

# Register one or more predefined consumers
system_hub.register_consumers(
    [push_consumer, mail_consumer, email_consumer]
)

# Register filters for the hubs
# By default, they accept any event
now = datetime.now()

user_hub.filter_by(
    WithSender("jorge") | WithReceivers(["jiri", "tibor"])
)

system_hub.filter_by(
    WithEventType("system") & Not(BeforeDate(now))
)


@app.route('/')
def index():
    return render_template("sse.html")


@app.route('/notify_user')
def notify_user_event():
    """Sends a notification of type user"""
    event = Event(event_id=None, event_type="user", title="This is a user test",
                  body="This is the body of the test", sender="jorge",
                  receivers=["jiri", "tibor"])
    notifications.send(event.to_json())

    return "Sent event"


@app.route('/notify_system')
def notify_system_event():
    """Sends a notification of type system"""
    event = Event(None, "system", "This is a system test",
                  "This is the body of the test", sender="system")
    notifications.send(event.to_json())

    return "Sent event"


@app.route("/user_notifications")
def user_notifier():
    """Propagate and push notifications"""
    return notifications.push_notifier_for(user_hub_id)


@app.route("/system_notifications")
def system_notifier():
    """Propagate and push notifications"""
    return notifications.push_notifier_for(system_hub_id)


if __name__ == '__main__':
    # Asynchronous server that allows to push SSE notifications
    server = WSGIServer(("0.0.0.0", 8080), app)
    server.serve_forever()
