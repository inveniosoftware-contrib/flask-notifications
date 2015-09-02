# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Event declaration for the Flask-Notifications module."""

import uuid
import time

from six.moves import UserDict
from flask.json import loads, dumps


class Event(UserDict):

    """Event is a signal which models a type of notification.

    It's fully customizable and allow to represent the business model
    by extending it.
    """

    def __init__(self, event_id, event_type, title, body,
                 timestamp=None, sender=None, recipients=[],
                 tags=[], expiration_datetime=None, **kwargs):
        """Initialize event and default non-existing values."""
        if not event_id:
            event_id = str(uuid.uuid4())

        if not timestamp:
            timestamp = time.time()

        d = {"event_id": event_id,
             "event_type": event_type,
             "title": title,
             "body": body,
             "timestamp": timestamp,
             "sender": sender,
             "recipients": recipients,
             "tags": tags,
             "expiration_datetime": expiration_datetime}

        UserDict.__init__(self, dict=d, **kwargs)

    def __str__(self):
        """By default, JSON."""
        return self.to_json()

    @classmethod
    def from_json(cls, event_json):
        """Json to event."""
        return cls(**loads(event_json))

    def to_json(self):
        """Event to json."""
        return dumps(self.data)
