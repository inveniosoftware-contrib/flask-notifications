#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from datetime import datetime

from flask_notifications.event_filter import EventFilter


class BeforeDate(EventFilter):

    def __init__(self, datetime):
        """Checks if a certain event has been emitted before
        a date.

        The date should be type of :class:`datetime.datetime`.
        """
        self.target_datetime = datetime

    def filter(self, event, *args, **kwargs):
        return datetime.fromtimestamp(event.timestamp) < self.target_datetime
