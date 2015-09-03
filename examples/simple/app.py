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
from flask import Flask, render_template
from redis import StrictRedis
from gevent.pywsgi import WSGIServer

from flask_celeryext import FlaskCeleryExt
from flask_notifications import Notifications
from flask_notifications.event import Event
from flask_notifications.filters import *
from flask_notifications.consumers.push.push_consumer import PushConsumer
from flask_notifications.consumers.email.flaskemail_consumer \
    import FlaskEmailConsumer
from flask_notifications.consumers.email.flaskmail_consumer \
    import FlaskMailConsumer

gevent.monkey.patch_all()

app = Flask(__name__)

# Get environment variables
default_redis_url = "redis://localhost:6379/0"
redis_url = os.environ.get("REDIS_URL") or default_redis_url
redis_host = redis_url.split(":")[1][2:]
smtp_server = os.environ.get("SMTP_SERVER") or "0.0.0.0"

default_email_account = "invnotifications@gmail.com"

config = {
    # Email configuration for Flask-Mail
    "MAIL_SERVER": smtp_server,
    "MAIL_PORT": "25",
    "MAIL_USERNAME": "",
    "MAIL_PASSWORD": "",
    "MAIL_DEBUG": True,

    # Email configuration for Flask-Email
    "EMAIL_HOST": smtp_server,
    "EMAIL_PORT": "25",
    "EMAIL_HOST_USER": "",
    "EMAIL_HOST_PASSWORD": "",

    "DEBUG": True,
    "CELERY_BROKER_URL": redis_url,
    "CELERY_RESULT_BACKEND": redis_url,
    "BROKER_TRANSPORT": "redis",
    "BROKER_URL": redis_url,
    "CELERY_ACCEPT_CONTENT": ["application/json"],
    "CELERY_TASK_SERIALIZER": "json",
    "CELERY_RESULT_SERIALIZER": "json",
    "REDIS_URL": redis_url,

    # Notifications configuration
    "BACKEND": "flask_notifications.backend.redis_backend.RedisBackend"
}

app.config.update(config)

celery = FlaskCeleryExt(app).celery
redis = StrictRedis(host=redis_host)

# Define our notifications extension
notifications = Notifications(app=app, celery=celery, broker=redis)

# Define the hubs for specific types of event
user_hub = notifications.create_hub("UserHub")
system_hub = notifications.create_hub("EventHub")
user_hub_id = user_hub.hub_id
system_hub_id = system_hub.hub_id


# Add a new consumer to the user_hub
@user_hub.register_consumer(name="app.write_to_file")
def write_to_file(event, *args, **kwargs):
    with open("events.log", "a+w") as f:
        f.write(str(event))


# Register manually a push consumer
backend = notifications.create_backend()
push_consumer = PushConsumer(backend, user_hub_id)
user_hub.register_consumer(push_consumer)

# Create two independent email consumers
mail_consumer = FlaskMailConsumer.from_app(
    app, default_email_account, [default_email_account]
)

email_consumer = FlaskEmailConsumer.from_app(
    app, default_email_account, [default_email_account]
)

# Register one or more predefined consumers
for consumer in (mail_consumer, email_consumer):
    system_hub.register_consumer(consumer)

# Register filters for the hubs
now = datetime.now()

user_hub.filter_by(
    WithSender("john") | WithRecipients(["tom", "tim"])
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
    event = Event(event_id=None, event_type="user",
                  title="This is a user test",
                  body="This is the body of the test", sender="john",
                  recipients=["tom", "tim"])
    notifications.send(event)

    return "Sent event"


@app.route('/notify_system')
def notify_system_event():
    """Sends a notification of type system"""
    event = Event(None, "system", "This is a system test",
                  "This is the body of the test", sender="system")
    notifications.send(event)

    return "Sent event"


@app.route("/user_notifications")
def user_notifier():
    """Propagate and push notifications"""
    return notifications.flask_sse_notifier(user_hub_id)


@app.route("/system_notifications")
def system_notifier():
    """Propagate and push notifications"""
    return notifications.flask_sse_notifier(system_hub_id)


if __name__ == '__main__':
    # Asynchronous server that allows to push SSE notifications
    server = WSGIServer(("0.0.0.0", 8080), app)
    server.serve_forever()
