# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""This extension allows creation of menus organised in a tree structure.

Those menus can be then displayed using templates.
"""

from celery import Celery
from flask import current_app, Response
from redis import StrictRedis
from werkzeug.local import LocalProxy

from flask.ext.notifications.consumers.consumers import Consumers
from flask.ext.notifications.event import Event, ExtendedJSONEncoder
from flask.ext.notifications.consumers.push.ssenotifier import SseNotifier
from .version import __version__


class NotificationService(object):
    """Flask extension implementing a Notification service."""

    def __init__(self, app=None, celery=None, redis=None, email_dependency=None):
        """
        Initializer of notification service

        :param app: Application to wrap
        :param celery: Optional celery instance to be used (it must be already set up with the proper config)
        :param redis: Optional redis instance to be used (it must be already set up with the proper config)
        :param email_dependency: Instance of EmailDependency with the function to send the emails usign different
                dependencies
        """
        self.app = app
        self.mail = None
        self.celery = None
        self.redis = None
        self._consumers = None
        self.email_dependency = None

        if app is not None:
            self.init_app(app, celery, redis, email_dependency)

    def init_app(self, app, celery=None, redis=None, email_dependency=None):
        """Initialization of the Flask-notifications extension."""
        self.app = app
        self.app.json_encoder = ExtendedJSONEncoder

        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'notification_service' in app.extensions:
            raise RuntimeError("Flask notification extension is already initialized.")

        # Celery dependency
        if celery is None:
            self.celery = Celery()
            self.celery.conf.update(app.config)
        else:
            self.celery = celery

        # Redis dependency (publisher-subscriber feature for SSE)
        if redis is None:
            self.redis = StrictRedis()
        else:
            self.redis = redis

        app.extensions['notification_service'] = self
        app.context_processor(lambda: dict(current_notification_service=current_notifications))

        self.email_dependency = email_dependency
        self._consumers = Consumers(self.celery, self.redis, self.email_dependency)

    def notify_all(self, event_json):
        event = Event.from_json(event_json)

        for consumer in self._consumers.all:
            consumer(event)

    def create_push_notifier(self):
        return Response(
            SseNotifier(self.redis.pubsub()),
            mimetype='text/event-stream'
        )

    @staticmethod
    def root():
        """Return a root entry of current application's menu."""
        return current_app.extensions['notification_service']


def notify(event_json):
    """Decorator of a view function that should propagate the notification
    to the consumers.

    Example::

        @notify(event_json)
        def index():
            pass

    :param event_json: JSON representation of the event to be notified.
    """

    def decorator(f):
        """Decorator of a view function that send notifications to the consumers
        in an asynchronous way."""
        event = Event.from_json(event_json)
        current_notifications.notify_all(event)

        return f

    return decorator


#: Global object that is proxy to the current application menu.
current_notifications = LocalProxy(NotificationService.root)

__all__ = ('current_notifications', 'notify', 'NotificationService', '__version__')
