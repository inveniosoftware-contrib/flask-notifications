# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from flask_notifications.pubsub.pubsub import PubSub


class RedisPubSub(PubSub):
    def __init__(self, redis):
        super(RedisPubSub, self).__init__(redis)
        self.pubsub = self.broker.pubsub()

    def publish(self, channel, event_json):
        """In Redis, this method will publish an event to a channel
        and that event will be received by any :class RedisPubSub:
        object which is subscribed to that channel."""
        return self.broker.publish(channel, event_json)

    def subscribe(self, channel):
        return self.pubsub.subscribe(channel)

    def listen(self):
        return self.pubsub.listen()
