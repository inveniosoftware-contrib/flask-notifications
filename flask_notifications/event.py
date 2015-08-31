# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

import uuid
import time

from UserDict import UserDict
from flask.json import loads, dumps


class Event(UserDict):

    """An Event is a signal used to specify a certain behaviour
    and is used to model types of notifications.

    It's fully customizable and allow to represent the business model
    by extending the event.
    """

    def __init__(self, event_id, event_type, title, body,
                 timestamp=None, sender=None, receivers=[],
                 tags=[], expiration_datetime=None, **kwargs):

        """Initialize event and default non-existing values."""

        # Randomizing ids if not present
        if not event_id:
            # Make a string out of a randomized uuid
            event_id = str(uuid.uuid4())

        if not timestamp:
            timestamp = time.time()

        d = {"event_id": event_id,
             "event_type": event_type,
             "title": title,
             "body": body,
             "timestamp": timestamp,
             "sender": sender,
             "receivers": receivers,
             "tags": tags,
             "expiration_datetime": expiration_datetime}

        UserDict.__init__(self, dict=d, **kwargs)

    @property
    def event_id(self):
        return self["event_id"]

    @property
    def event_type(self):
        return self["event_type"]

    @property
    def title(self):
        return self["title"]

    @property
    def body(self):
        return self["body"]

    @property
    def timestamp(self):
        return self["timestamp"]

    @property
    def sender(self):
        return self["sender"]

    @property
    def receivers(self):
        return self["receivers"]

    @property
    def tags(self):
        return self["tags"]

    @property
    def expiration_datetime(self):
        return self["expiration_datetime"]

    def __str__(self):
        return self.to_json()

    @classmethod
    def from_json(cls, event_json):
        return cls(**loads(event_json))

    def to_json(self):
        return dumps(self.data)
