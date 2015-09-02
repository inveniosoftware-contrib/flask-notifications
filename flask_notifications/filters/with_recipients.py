# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""WithRecipients filter declaration."""

from flask_notifications.event_filter import EventFilter


class WithRecipients(EventFilter):

    """Filter that checks that all the recipients meet the given ones."""

    def __init__(self, target_recipients):
        """Initialise filter."""
        self.target_recipients = set(target_recipients)

    def filter(self, event, *args, **kwargs):
        """Check that all the recipients are included in the event."""
        set_recipients = set(event["recipients"])
        return len(set_recipients ^ self.target_recipients) == 0
