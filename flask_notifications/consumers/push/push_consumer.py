# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""PushConsumer that push messages to a broker."""

from flask_notifications.consumers.consumer import Consumer


class PushConsumer(Consumer):
    """Publish to a channel using a Backend without knowing the broker."""

    def __init__(self, redis, hub_id):
        """Initialise redis and the hub_id."""
        self.redis = redis
        self.hub_id = hub_id

    def consume(self, event_json, *args, **kwargs):
        """Publish an event to a channel named with the hub_id."""
        return self.redis.publish(self.hub_id, str(event_json))
