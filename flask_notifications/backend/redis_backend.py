# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""RedisBackend declaration."""

from flask_notifications.backend.backend import Backend


class RedisBackend(Backend):
    """Backend implementation using Redis."""

    def __init__(self, redis):
        """Initialise and call base class."""
        super(RedisBackend, self).__init__(redis)
        self.pubsub = self.broker.pubsub()

    def publish(self, channel, event_json):
        """Publish an event to a channel.

        That event will be received by any :class RedisBackend:
        object which is subscribed to that channel.
        """
        return self.broker.publish(channel, event_json)

    def subscribe(self, channel):
        """Subscribe to a channel."""
        return self.pubsub.subscribe(channel)

    def listen(self):
        """Listen to a channel."""
        return self.pubsub.listen()
