# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Base class for a Publish/Subscribe implementation in any broker."""

import abc


class Backend(object):
    """Allows to publish, subscribe and listen to events."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, broker):
        """Initialise broker."""
        self.broker = broker

    @abc.abstractmethod
    def publish(self, channel, event):
        """Publish an event to a channel."""
        pass

    @abc.abstractmethod
    def subscribe(self, channel):
        """Subscribe to a channel only for this object.

        The :method listen: will receive the published event to
        the channel.
        """
        pass

    @abc.abstractmethod
    def listen(self):
        """Listen to all the subscribed channels in this object."""
        pass
