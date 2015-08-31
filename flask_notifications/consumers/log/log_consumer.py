#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from flask_notifications.consumers.consumer import Consumer


class LogConsumer(Consumer):

    """Log to a file an event."""

    def __init__(self, filepath="events.log"):
        """Initialise permissions and filepath."""
        self.filepath = filepath
        # Permission to read, write and create
        self.default_permissions = "a+w"

    def consume(self, event_json, *args, **kwargs):
        """Write event to file."""
        with open(self.filepath, self.default_permissions) as f:
            f.write(str(event_json))
