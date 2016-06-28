# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Declaration of filters for the events."""

from abc import ABCMeta, abstractmethod


class EventFilter(object):
    """Filter that represents a certain condition for the events.

    One can compose event filters with the following bitwise operators:
        :method &: AND bitwise operator
        :method |: OR bitwise operator
        :method ^: XOR bitwise operator
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def filter(self, event, *args, **kwargs):
        """Logic of the filter. It should always return a Boolean."""
        pass

    def __call__(self, event, *args, **kwargs):
        """By default, execute filter method."""
        return self.filter(event, args, kwargs)

    def __and__(self, other):
        """Compose filters with &."""
        return AndFilter(self, other)

    def __or__(self, other):
        """Compose filters with |."""
        return OrFilter(self, other)

    def __xor__(self, other):
        """Compose filters with ^."""
        return XorFilter(self, other)


class ComposedFilter(EventFilter):
    """Interface for operators between filters."""

    def __init__(self, one, other):
        """Initialise both filters."""
        self.one = one
        self.other = other


class AndFilter(ComposedFilter):
    """Filter implementing the AND logic between two filters."""

    def filter(self, event, *args, **kwargs):
        """AND logic."""
        return (self.one.__call__(event, args, kwargs) and
                self.other.__call__(event, args, kwargs))


class OrFilter(ComposedFilter):
    """Filter implementing the OR logic between two filters."""

    def filter(self, event, *args, **kwargs):
        """OR logic."""
        return (self.one.__call__(event, args, kwargs) or
                self.other.__call__(event, args, kwargs))


class XorFilter(ComposedFilter):
    """Filter implementing the XOR logic between two filters."""

    def filter(self, event, *args, **kwargs):
        """XOR logic."""
        return (self.one.__call__(event, args, kwargs) ^
                self.other.__call__(event, args, kwargs))
