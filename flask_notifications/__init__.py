# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""This extension is a Notification service that allows to send
notifications given some events as an input. The notifications arrive
to the users using predefined or custom consumers.
"""

from celery import Celery
from flask import current_app, Response
from redis import StrictRedis
from werkzeug.local import LocalProxy

from flask.ext.notifications.event import Event
from flask.ext.notifications.consumers.push.ssenotifier import SseNotifier
from flask.ext.notifications.event_hub import EventHub
from .version import __version__


class Notifications(object):

    """Flask extension implementing a Notification service."""

    def __init__(self, app=None, celery=None, redis=None,
                 redis_url=None, *args, **kwargs):
        """Initializer of the notification service.

        :param app: Application to extend
        :param celery: Optional celery instance to be used (it must
                        be already set up with the proper config)
        :param redis: Optional redis instance to be used (it must be
                        already set up with the proper config)
        :param redis_url: If no redis instance is passed, initialise
                          a new one with the given redis_url
        """
        self.app = app
        self.mail = None
        self.celery = None
        self.redis = None
        self._hubs = {}
        self._notifiers = {}

        if app is not None:
            self.init_app(app, celery, redis, *args, **kwargs)

    def init_app(self, app, celery=None, redis=None, redis_url=None,
                 *args, **kwargs):
        """Initialization of the Flask-notifications extension."""
        self.app = app

        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'notifications' in app.extensions:
            raise RuntimeError("Flask notification extension is "
                               "already initialized.")

        # Celery dependency, useful to avoid the user to pass
        # this instance when declaring an EventHub
        if celery is None:
            self.celery = Celery()
            self.celery.conf.update(app.config)
        else:
            self.celery = celery

        # Redis dependency (publisher-subscriber feature for SSE)
        if redis is None:
            self.redis = StrictRedis(redis_url if redis_url else "")
        else:
            self.redis = redis

        app.extensions['notifications'] = self

        app.context_processor(
            lambda: dict(current_notifications=current_notifications)
        )

    def send(self, event_json):
        """Send an event through all the hubs."""
        event = Event.from_json(event_json)

        for hub_name, hub in self._hubs.iteritems():
            # Be careful, operation order matters here
            hub.consume(event)

    def push_notifier_for(self, hub_id):
        """
        Create a Flask Response that will push notifications
        to the client once they are propagated through the system.

        :return: A :class Response: that push new notifications
                 to the browsers
        """
        push_notifier = self._notifiers.get(hub_id)

        if not push_notifier:
            push_notifier = Response(
                SseNotifier(self.redis.pubsub(), hub_id),
                mimetype='text/event-stream'
            )

            self._notifiers[hub_id] = push_notifier

        return push_notifier

    def create_hub(self):
        """
        Create a EventHub to aggregate certain types of events that will
        be consumed by the defined consumers in the hub.

        :return: An :class EventHub: to register consumers and filters
        """
        hub = EventHub(self.celery)
        self._hubs[hub.hub_id] = hub

        return hub

    @staticmethod
    def root():
        """Return a root entry of current application's menu."""
        return current_app.extensions['notifications']


#: Global object that is proxy to the current application menu.
current_notifications = LocalProxy(Notifications.root)

__all__ = ('current_notifications', 'notify', 'Notifications', '__version__')
