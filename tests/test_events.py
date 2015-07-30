# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

import unittest
from celery import Celery
from flask import Flask
from flask.json import dumps
import os
from redis import StrictRedis, Redis
from flask.ext.notifications import Notifications, Event
from flask.ext.notifications.consumers.email.flaskmail_consumer import \
    FlaskMailConsumer
from flask.ext.notifications.consumers.push.push_consumer import PushConsumer


class NotificationsFlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.test_app = self.app.test_client()

        self.config = {
            # Email configuration for Flask-Mail
            "MAIL_SERVER": "smtp.gmail.com",
            "MAIL_PORT": "587",
            "MAIL_USERNAME": "invnotifications@gmail.com",
            "MAIL_PASSWORD": os.environ["INVENIO_GMAIL_PASSWORD"],
            "MAIL_USE_TLS": True,
            "MAIL_USE_SSL": False,

            "DEBUG": True,
            "TESTING": True,
            "CELERY_BROKER_URL": "redis://localhost:6379/0",
            "CELERY_RESULT_BACKEND": "redis://localhost:6379/0",
            "BROKER_TRANSPORT": "redis",
            "CELERY_ACCEPT_CONTENT": ["pickle", "json"],
            "CELERY_ALWAYS_EAGER": True,
            "REDIS_URL": "redis://localhost:6379/0"
        }

        self.app.config.update(self.config)
        self.celery = Celery()
        self.celery.conf.update(self.config)
        default_email_account = "invnotifications@gmail.com"
        self.flaskmail = FlaskMailConsumer.from_app(self.app,
                                                    default_email_account,
                                                    [default_email_account])
        self.redis = Redis()
        self.notifications = Notifications(app=self.app,
                                           celery=self.celery,
                                           redis=self.redis)

    def blocking_get_message(self, pubsub):
        response = pubsub.parse_response(block=True)
        if response:
            return pubsub.handle_message(response,
                                         ignore_subscribe_messages=False)
        return None

    def tearDown(self):
        self.app = None
        self.celery = None
        self.redis = None


class EventsTest(NotificationsFlaskTestCase):
    def test_json_parser(self):
        with self.app.test_request_context():
            event = Event(event_id="1",
                          event_type="type",
                          title="This is a test",
                          body="This is the body of a test")

            json = event.to_json()
            event_from_parser = Event.from_json(json)

            assert event_from_parser.event_id == event.event_id
            assert event_from_parser.title == event.title
            assert event_from_parser.body == event.body


class EmailNotificationTest(NotificationsFlaskTestCase):
    def test_email_delivery(self):
        with self.app.test_request_context():
            event = Event(event_id="1",
                          event_type="type",
                          title="This is a test",
                          body="This is the body of a test")
            email_function = self.flaskmail

            # Testing only the synchronous execution, not async
            with self.flaskmail.mail.record_messages() as outbox:
                email_function(event)
                assert len(outbox) == 1
                assert outbox[0].subject == "Event {0}".format(
                    event["event_id"])
                assert outbox[0].body == str(event)


# This test is not passing, need fix
class PushNotificationTest(NotificationsFlaskTestCase):
    def test_push(self):
        """
        Testing if the predefined PushConsumer works properly.
        """
        with self.app.test_request_context():
            push_function = PushConsumer(self.redis)

            pubsub = self.notifications.create_push_notifier_for("user") \
                .response.pubsub

            event = Event(
                "1", "user", "This is a test", "This is the body of a test"
            )

            push_function.consume(event)

            # Popping subscribe message. Somehow, if the option
            # ignore_subscribe_messages is true, the other messages
            # are not detected.
            propagated_message = self.blocking_get_message(pubsub)

            # Getting expected message and checking if it's the sent event
            propagated_message = self.blocking_get_message(pubsub)
            assert propagated_message['data'] == str(event)


if __name__ == '__main__':
    unittest.main()
