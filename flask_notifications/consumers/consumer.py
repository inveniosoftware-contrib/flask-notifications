# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Consumer declaration."""

import abc


class Consumer(object):

    """A callable that performs an action when receives an event.

    A user can define his own hooks for each consumer. Two hooks
    are available: before and after consuming.
    """

    __metaclass__ = abc.ABCMeta

    def __call__(self, event_json, *args, **kwargs):
        """Main logic of the consumer."""
        # Executing hook before consuming
        self.before_consume(event_json, *args, **kwargs)

        consumed = self.consume(event_json, *args, **kwargs)

        # Executing hook after consuming
        self.after_consume(event_json, *args, **kwargs)

        return consumed

    def before_consume(event_json, *args, **kwargs):
        """Optional hook to be executed before :method consume:."""
        pass

    def after_consume(event_json, *args, **kwargs):
        """Optional hook to be executed after :method consume:."""
        pass

    @abc.abstractmethod
    def consume(self, event_json, *args, **kwargs):
        """Real logic of the consumer."""

    @property
    def __name__(self):
        """Get name of class."""
        return self.__class__.__name__

    def __hash__(self):
        """Hash only using the name and not the id.

        To avoid duplicate recipients in a hub, we redefine the
        hash to be unique for the same Consumer.
        """
        return hash(self.__name__)

    def __eq__(self, other):
        """Equality comparison only using hash."""
        return hash(self) == hash(other)
