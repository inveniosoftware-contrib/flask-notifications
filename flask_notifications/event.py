#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from UserDict import UserDict

from flask.json import loads, dumps


class Event(UserDict):
    """
    This class models an event (notification) used to signal to the API which behaviour
    should adopt.
    """

    def __init__(self, event_id, event_type, title, body, **kwargs):
        d = {"event_id": event_id,
             "event_type": event_type,
             "title": title,
             "body": body}

        UserDict.__init__(self, dict=d, **kwargs)

        self.event_id = self["event_id"]
        self.event_type = self["event_type"]
        self.title = self["title"]
        self.body = self["body"]

    def __str__(self):
        return "Event {0}({1}): {2}\n".format(self.event_id,
                                              self.event_type,
                                              self.title,
                                              self.body)

    @classmethod
    def from_json(cls, event_json):
        return cls(**loads(event_json))

    def to_json(self):
        return dumps(self.data)
