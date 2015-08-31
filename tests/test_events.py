# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

import os
import unittest
from datetime import datetime
from datetime import timedelta

from celery import Celery
from flask import Flask
from redis import StrictRedis

from flask.ext.email import DummyMail
from flask.ext.email import SMTPMail

from flask_notifications import Notifications
from flask_notifications.event import Event
from flask_notifications.event_hub import EventHub
from flask_notifications.consumers.email.flaskmail_consumer import \
    FlaskMailConsumer
from flask_notifications.consumers.email.flaskemail_consumer import \
    FlaskEmailConsumer
from flask_notifications.consumers.push.push_consumer import PushConsumer
from flask_notifications.consumers.log.log_consumer import LogConsumer
from flask_notifications.filters.before_date import BeforeDate
from flask_notifications.filters.expired import Expired
from flask_notifications.filters.with_id import WithId
from flask_notifications.filters.with_sender import WithSender
from flask_notifications.filters.with_receivers import WithReceivers
from flask_notifications.filters.with_event_type import WithEventType
from flask_notifications.filters.not_filter import Not


class NotificationsFlaskTestCase(unittest.TestCase):

    """Base test class for Flask-Notifications."""

    def setUp(self):
        """Set up the environment before the tests."""
        self.app = Flask(__name__)
        self.test_app = self.app.test_client()

        self.config = {
            "DEBUG": True,
            "TESTING": True,
            "CELERY_BROKER_URL": "redis://localhost:6379/0",
            "CELERY_RESULT_BACKEND": "redis://localhost:6379/0",
            "BROKER_TRANSPORT": "redis",
            "CELERY_ACCEPT_CONTENT": ["application/json"],
            "CELERY_TASK_SERIALIZER": "json",
            "CELERY_RESULT_SERIALIZER": "json",
            "CELERY_ALWAYS_EAGER": True,
            "REDIS_URL": "redis://localhost:6379/0",

            # Notifications configuration
            "PUBSUB": "flask_notifications.pubsub.redis_pubsub.RedisPubSub"
        }

        # Set up the instances
        self.app.config.update(self.config)
        self.celery = Celery()
        self.celery.conf.update(self.config)
        self.redis = StrictRedis()

        # Get instance of the notifications module
        self.notifications = Notifications(
            app=self.app, celery=self.celery, broker=self.redis
        )

        self.pubsub = self.notifications.create_pubsub()

        # Mail settings
        self.default_email_account = "invnotifications@gmail.com"

        # Time variables
        self.tomorrow = datetime.now() + timedelta(days=1)
        next_to_tomorrow = datetime.now() + timedelta(days=2)
        self.next_to_tomorrow_tm = float(next_to_tomorrow.strftime("%s"))

        # Create basic event to use in the tests, id randomized
        self.event = Event("1234",
                           event_type="user",
                           title="This is a test",
                           body="This is the body of a test",
                           sender="system",
                           receivers=["jvican"],
                           expiration_datetime=self.tomorrow)
        self.event_json = self.event.to_json()

    def tearDown(self):
        """Destroy environment."""
        self.app = None
        self.celery = None
        self.redis = None


class EventsTest(NotificationsFlaskTestCase):

    def test_json_parser(self):
        """Is to_json and from_json working correctly?"""

        with self.app.test_request_context():
            json = self.event.to_json()
            event_from_parser = Event.from_json(json)

            assert event_from_parser.event_id == self.event.event_id
            assert event_from_parser.title == self.event.title
            assert event_from_parser.body == self.event.body


class FlaskMailNotificationTest(NotificationsFlaskTestCase):

    def setUp(self):
        super(FlaskMailNotificationTest, self).setUp()

        # Use flask-mail dependency
        self.flaskmail = FlaskMailConsumer.from_app(
            self.app, self.default_email_account, [self.default_email_account]
        )

    def test_email_delivery(self):
        with self.app.test_request_context():
            email_consumer = self.flaskmail

            # Testing only the synchronous execution, not async
            with self.flaskmail.mail.record_messages() as outbox:
                # Send email
                email_consumer(self.event_json)

                expected = "Event {0}".format(self.event.event_id)

                assert len(outbox) == 1
                assert outbox[0].subject == expected
                assert outbox[0].body == self.event_json


class FlaskEmailNotificationTest(NotificationsFlaskTestCase):

    def setUp(self):
        super(FlaskEmailNotificationTest, self).setUp()

        # Use flask-email dependency (with DummyMail for testing)
        self.flaskemail = FlaskEmailConsumer(
            DummyMail(self.app), self.default_email_account,
            [self.default_email_account]
        )

    def test_email_delivery(self):
        with self.app.test_request_context():
            email_consumer = self.flaskemail
            assert email_consumer(self.event_json) != 0

    def test_from_app(self):
        with self.app.test_request_context():
            flaskemail_instance = FlaskEmailConsumer.from_app(
                self.app, self.default_email_account,
                [self.default_email_account]
            )

            # Test from_app method create a SMTP mailbox by default
            assert isinstance(flaskemail_instance.mail, SMTPMail)


class PushNotificationTest(NotificationsFlaskTestCase):

    def test_push(self):
        """Test if PushConsumer works properly."""

        with self.app.test_request_context():
            user_hub = EventHub("TestPush", self.celery)
            user_hub_id = user_hub.hub_id
            push_function = PushConsumer(self.pubsub, user_hub_id)

            # The notifier that push notifications to the client via SSE
            sse_notifier = self.notifications.sse_notifier_for(user_hub_id)

            push_function.consume(self.event_json)

            # Popping subscribe message. Somehow, if the option
            # ignore_subscribe_messages is True, the other messages
            # are not detected.
            propagated_messages = sse_notifier.pubsub.listen()
            print(propagated_messages)
            message = propagated_messages.next()

            # Getting expected message and checking it with the sent one
            message = propagated_messages.next()
            assert message['data'] == self.event_json


class LogNotificationTest(NotificationsFlaskTestCase):

    def test_log(self):
        """Test if LogConsumer works properly."""
        with self.app.test_request_context():
            filepath = "events.log"

            # Clean previous log files and log to file
            if os.access(filepath, os.R_OK):
                os.remove(filepath)
            log_function = LogConsumer(filepath)
            log_function.consume(self.event_json)

            # Check and remove file
            with open(filepath, "r") as f:
                written_line = f.readline()
                assert written_line == self.event_json
            os.remove(filepath)


class EventHubAndFiltersTest(NotificationsFlaskTestCase):

    def setUp(self):
        super(EventHubAndFiltersTest, self).setUp()

        self.event_hub = EventHub("TestFilters", self.celery)
        self.event_hub_id = self.event_hub.hub_id

    def test_register_consumer(self):
        """
        The client can register consumers using a decorator or
        calling directly :method register_consumer:. The client also
        can deregister consumers.
        """
        @self.event_hub.consumer()
        def write_to_file(event_json, *args, **kwargs):
            f = open("events.log", "a+w")
            f.write(event_json)

        push_consumer = PushConsumer(self.pubsub, self.event_hub_id)
        self.event_hub.register_consumer(PushConsumer)

        # The previous consumers are indeed registered
        assert self.event_hub.is_registered(push_consumer) is True
        assert self.event_hub.is_registered(write_to_file) is True

        # Registering the same PushConsumer as a sequence of consumers
        repeated_push_consumer = PushConsumer(self.pubsub, self.event_hub_id)
        self.event_hub.register_consumers([PushConsumer])

        # The previous operation has no effect as the consumer has
        # been previously registered
        registered = list(self.event_hub.registered_consumers)

        def check_registered_consumer(c):
            return c == repeated_push_consumer.__name__

        assert len(filter(check_registered_consumer, registered)) == 1

        # Deregister previous consumers
        self.event_hub.deregister_consumers([write_to_file, push_consumer])
        assert len(self.event_hub.registered_consumers) == 0

    def test_and_filters(self):
        f1 = WithEventType("user")
        f2 = WithSender("system")
        f3 = WithReceivers(["jvican"])

        f1f2 = f1 & f2
        f1f2f3 = f1 & f2 & f3

        assert f1f2f3(self.event) is True

        assert f1(self.event) is True
        self.event.event_type = "info"
        assert f1(self.event) is False
        assert f1f2(self.event) is False
        assert f1f2f3(self.event) is False

        assert f2(self.event) is True
        self.event.sender = "antisystem"
        assert f2(self.event) is False
        assert f1f2f3(self.event) is False

        assert f3(self.event) is True
        self.event.receivers = ["johndoe"]
        assert f3(self.event) is False
        assert f1f2f3(self.event) is False

    def test_or_filters(self):
        f1 = BeforeDate(self.tomorrow)
        f2 = WithId("1234")
        f3 = Not(Expired())
        f1f2f3 = f1 | f2 | f3

        assert f1f2f3(self.event) is True

        assert f1(self.event) is True
        self.event.timestamp = self.next_to_tomorrow_tm
        assert f1(self.event) is False
        assert f1f2f3(self.event) is True

        assert f2(self.event) is True
        self.event.event_id = "123"
        assert f2(self.event) is False
        assert f1f2f3(self.event) is True

        assert f3(self.event) is True
        self.event.expiration_datetime = datetime.now()
        assert f3(self.event) is False
        assert f1f2f3(self.event) is False


if __name__ == '__main__':
    unittest.main()
