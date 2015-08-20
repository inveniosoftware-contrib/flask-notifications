#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.
from flask.ext.notifications.consumers.consumer import Consumer


class PushConsumer(Consumer):
    def __init__(self, redis, hub_id):
        # Redis dependency
        self.redis = redis
        self.hub_id = hub_id

    def consume(self, event, *args, **kwargs):
        self.redis.publish(self.hub_id, str(event))
