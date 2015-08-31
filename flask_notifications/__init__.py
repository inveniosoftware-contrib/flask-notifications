# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""This extension is a Notification service that allows to send
real-time notifications to the users.
"""

from importlib import import_module

from flask import current_app, Response
from flask_celeryext import FlaskCeleryExt
from werkzeug.local import LocalProxy

from flask_notifications.consumers.push.ssenotifier import SseNotifier
from flask_notifications.event_hub import EventHub
from .version import __version__


class Notifications(object):

    """Flask extension implementing a Notification service."""

    def __init__(self, app=None, celery=None, broker=None, *args, **kwargs):
        """Initialize the notification service.

        :param app: Application to extend
        :param celery: Optional celery instance to be used (it must
                        be already set up with the proper config)
        :param broker: Optional broker instance to be used (it must be
                        already set up with the proper config)
        """
        self.app = app
        self.celery = celery
        self.broker = broker
        self._hubs = {}
        self._notifiers = {}

        if app is not None:
            self.init_app(app, celery, broker, *args, **kwargs)

    def init_app(self, app, celery=None, broker=None, *args, **kwargs):
        """Initialization of the Flask-notifications extension."""
        self.app = app

        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'notifications' in app.extensions:
            raise RuntimeError("Flask notification extension is "
                               "already initialized.")

        # Celery dependency
        if celery is None:
            self.celery = FlaskCeleryExt(app)
        else:
            self.celery = celery

        # Broker dependency, mandatory
        self.broker = broker

        # Dynamic import from class name of pubsub
        default_pubsub = "flask_notifications.pubsub.redis_pubsub.RedisPubSub"
        pubsub_option = self.app.config["PUBSUB"] or default_pubsub
        pubsub_option = pubsub_option.split(".")
        module, classname = pubsub_option[0:-1], pubsub_option[-1]

        imported_module = import_module(".".join(module))
        self.pubsub = getattr(imported_module, classname)

        # Register extension in Flask app
        app.extensions['notifications'] = self

        app.context_processor(
            lambda: dict(current_notifications=current_notifications)
        )

    def send(self, event):
        """Send an event through to all the hubs."""
        def consume(hub):
            hub.consume(event)
        map(consume, self._hubs.itervalues())

    def sse_notifier_for(self, hub_id):
        """Create a :class SseNotifier: listening to a hub."""
        try:
            sse_notifier = self._notifiers[hub_id]
        except KeyError:
            sse_notifier = SseNotifier(self.create_pubsub(), hub_id)
            self._notifiers[hub_id] = sse_notifier

        return sse_notifier

    def flask_sse_notifier(self, hub_id):
        """Create a Flask :class Response: that will push notifications
        to the client once they are propagated through the system.
        """
        return Response(self.sse_notifier_for(hub_id),
                        mimetype='text/event-stream')

    def create_hub(self, hub_alias):
        """Create an EventHub to aggregate certain types of events that will
        be consumed by the defined consumers in the hub.
        """
        hub = EventHub(hub_alias, self.celery)
        self._hubs[hub.hub_id] = hub
        return hub

    def create_pubsub(self):
        """Return a PubSub instance from the class specified in
        the PUBSUB option.
        """
        return self.pubsub(self.broker)

    @staticmethod
    def root():
        """Return a root entry of current application's menu."""
        return current_app.extensions['notifications']


current_notifications = LocalProxy(Notifications.root)

__all__ = ('current_notifications', 'Notifications', '__version__')
