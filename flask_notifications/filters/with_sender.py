# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""WithSender filter declaration."""

from flask_notifications.event_filter import EventFilter


class WithSender(EventFilter):

    """Filter that checks the sender of an event with a given one."""

    def __init__(self, target_sender):
        """Initialise filter."""
        self.target_sender = target_sender

    def filter(self, event, *args, **kwargs):
        """Check the sender of the event."""
        return event["sender"] == self.target_sender
