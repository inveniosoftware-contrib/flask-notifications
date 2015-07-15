import unittest
from celery import Celery
from flask import Flask
from flask.json import jsonify, dumps
from flask.ext.notifications import NotificationService, Event


class EventsTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        self.config = {
            "MAIL_SERVER": "smtp.gmail.com",
            "MAIL_PORT": "587",
            "MAIL_USERNAME": "invnotifications@gmail.com",
            "MAIL_PASSWORD": "invenio888",
            "MAIL_USE_TLS": True,
            "MAIL_USE_SSL": False,
            "CELERY_BROKER_URL": "redis://localhost:6379/0",
            "CELERY_RESULT_BACKEND": "redis://localhost:6379/0",
            "BROKER_TRANSPORT": "redis",
            "CELERY_ACCEPT_CONTENT": ["pickle", "json"],
            "REDIS_URL": "redis://localhost:6379/0",
            "TESTING": True,
            "DEBUG": True
        }

        self.app.config = self.config
        self.celery = Celery()
        self.celery.conf.update(self.config)
        self.notifications = NotificationService(app=self.app, celery=self.celery)

    def test_json_parser(self):
        with self.app.test_request_context():
            event = Event("1", "This is a test", "This is the body of a test")
            json = dumps(event)
            event_from_parser = Event.from_json(json)

            assert event_from_parser.event_id == event.event_id
            assert event_from_parser.title == event.title
            assert event_from_parser.body == event.body


if __name__ == '__main__':
    unittest.main()
