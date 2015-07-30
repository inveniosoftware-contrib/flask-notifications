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
from blinker import signal

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

    def __init__(self, app=None, celery=None, redis=None, redis_url=None,
                 *args, **kwargs):
        """
        Initializer of notification service

        :param app: Application to wrap
        :param celery: Optional celery instance to be used (it must
                        be already set up with the proper config)
        :param redis: Optional redis instance to be used (it must be
                        already set up with the proper config)
        :param email_dependency: Instance of EmailDependency with the
                        function to send the emails using different dependencies
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
        if 'notification_service' in app.extensions:
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
            self.redis = StrictRedis(redis_url if redis_url is not None else "")
        else:
            self.redis = redis

        app.extensions['notification_service'] = self

        app.context_processor(
            lambda: dict(current_notification_service=current_notifications)
        )

    def notify(self, event_json):
        event = Event.from_json(event_json)
        sent = False

        assigned_hub = self._hubs[event.event_type]
        if assigned_hub is not None:
            assigned_hub.consume(event)
            sent = True

        return sent

    def create_push_notifier_for(self, event_type):
        """
        Create a Response that will push notifications to the client once they
        are propagated through the system.
        """
        push_notifier = self._notifiers.get(event_type)

        if push_notifier is None:
            push_notifier = Response(
                SseNotifier(self.redis.pubsub(), event_type),
                mimetype='text/event-stream'
            )

            self._notifiers[event_type] = push_notifier

        return push_notifier

    def hub_for(self, signal_name):
        """
        Create a EventHub to register consumers that will apply only for
        an specific type of an event.

        :param signal_name: The event type you want to process

        :return: An EventHub you can use to declare consumers
        """
        hub = EventHub(signal_name, self.celery)
        self._hubs[signal_name] = hub
        return hub

    @staticmethod
    def root():
        """Return a root entry of current application's menu."""
        return current_app.extensions['notification_service']


#: Global object that is proxy to the current application menu.
current_notifications = LocalProxy(Notifications.root)

__all__ = ('current_notifications', 'notify', 'Notifications', '__version__')
