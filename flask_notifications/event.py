# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Event declaration for the Flask-Notifications module."""

import uuid
import time
import datetime

from jsonschema import Draft4Validator, FormatChecker
from six.moves import UserDict
from flask.json import loads, dumps


class Event(UserDict):
    """Event is a signal which models a type of notification.

    It's fully customizable and allow to represent the business model
    by extending it.
    """

    schema = {
        "$schema": "http://json-schema.org/schema#",
        "type": "object",
        "properties": {
            "event_id": {"type": "string"},
            "event_type": {"type": "string"},
            "title": {"type": "string"},
            "body": {"type": "string"},
            "timestamp": {"type": "number"},
            "sender": {"type": "string"},
            "recipients": {"type": "array"},
            "tags": {"type": "array"},
            "expiration_datetime": {
                "type": ["datetime", "null"],
            },
        },
        "required": [
            "event_id", "event_type", "title",
            "body", "timestamp", "sender", "recipients",
            "tags", "expiration_datetime"
        ],
    }

    def __init__(self, event_id, event_type, title, body,
                 timestamp=None, sender="", recipients=[],
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

        validator = Draft4Validator(Event.schema,
                                    types={"datetime": (datetime.datetime)},
                                    format_checker=FormatChecker())
        validator.validate(self.data)

    def __str__(self):
        """By default, JSON."""
        return self.to_json()

    @staticmethod
    def to_datetime(dt_format):
        """Get datetime from default string format.

        If you use your own format for the datetime, override this method
        to match your datetimes. Otherwise, they won't be validated.
        """
        datetime_format = "%a, %d %b %Y %H:%M:%S GMT"
        return datetime.datetime.strptime(dt_format, datetime_format)

    @classmethod
    def from_json(cls, event_json):
        """Json to event."""
        d = loads(event_json)
        expiration = d["expiration_datetime"]
        if expiration:
            # By default, datetime are not decoded correctly
            d["expiration_datetime"] = cls.to_datetime(expiration)
        return cls(**d)

    def to_json(self):
        """Event to json."""
        return dumps(self.data)
