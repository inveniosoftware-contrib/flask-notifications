#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

import abc
from celery import Task


class Consumer(object):
    __metaclass__ = abc.ABCMeta

    def __call__(self, event, *args, **kwargs):
        return self.consume(event)

    @abc.abstractmethod
    def consume(self, event, *args, **kwargs):
        """
        This method is the logic of the consumer.
        """

    @property
    def __name__(self):
        return self.__class__.__name__
