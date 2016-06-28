# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Notifier that uses Server-Sent Events."""

from sse import Sse


class SseNotifier(object):
    """Iterator that yields the published messages in a channel."""

    def __init__(self, backend, channel):
        """Initialise PublishSubscribe instance and channel."""
        self.sse = Sse()
        self.backend = backend
        self.backend.subscribe(channel)

    def __iter__(self):
        """Yield the published messages in a SSE format."""
        for message in self.backend.listen():
            if message['type'] == 'message':
                self.sse.add_message("", message['data'])
                for data in self.sse:
                    yield data.encode('u8')
