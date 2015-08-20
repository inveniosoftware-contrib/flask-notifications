#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from flask_notifications.event_filter import EventFilter


class WithId(EventFilter):

    def __init__(self, target_id):
        self.target_id = target_id

    def filter(self, event, *args, **kwargs):
        return event.event_id == self.target_id
