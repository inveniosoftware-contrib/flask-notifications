#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from flask_notifications.event_filter import EventFilter


class WithReceivers(EventFilter):

    def __init__(self, target_receivers):
        self.target_receivers = set(target_receivers)

    def filter(self, event, *args, **kwargs):
        set_receivers = set(event.receivers)
        return len(set_receivers ^ self.target_receivers) == 0
