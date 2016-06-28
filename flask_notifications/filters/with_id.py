# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""WithID filter declaration."""

from flask_notifications.event_filter import EventFilter


class WithId(EventFilter):
    """Filter that checks the id of an event."""

    def __init__(self, target_id):
        """Initialise filter."""
        self.target_id = target_id

    def filter(self, event, *args, **kwargs):
        """Check event type."""
        return event["event_id"] == self.target_id
