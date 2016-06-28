# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""BeforeDate filter declaration."""

from datetime import datetime

from flask_notifications.event_filter import EventFilter


class BeforeDate(EventFilter):
    """Filter that checks the event date is before a given date."""

    def __init__(self, datetime):
        """Check a certain event has been emitted before a date.

        The date should be type of :class datetime.datetime:.
        """
        self.target_datetime = datetime

    def filter(self, event, *args, **kwargs):
        """Check both dates."""
        return (datetime.fromtimestamp(event["timestamp"]) <
                self.target_datetime)
