# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Always filter declaration."""

from flask_notifications.event_filter import EventFilter


class Always(EventFilter):
    """Filter that accepts any event."""

    def filter(self, event, *args, **kwargs):
        """It is always true."""
        return True
