#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from blinker import signal


class EventHub:
    def __init__(self, signal_name, celery):
        """
        Inits the Hub with a signal name and Celery to perform async execution
        """
        self.signal = signal(signal_name)
        self.celery = celery

    def consumer(self):
        """
        Decorator that modifies the given function, makes it
        asynchronous and connect the function to the signal.
        """

        # Making the function asynchronous
        def async_consumer(f):
            async_creator = self.celery.task()
            async_f = async_creator(f)
            # Connecting the async function to the signal
            # No sender restriction for the moment
            self.signal.connect(async_f.delay, weak=False)

            return f

        return async_consumer

    def consumers(self, consumers):
        """
        Register one or more consumers from an iterable of
        predefined consumers.
        """
        consumer_creator = self.consumer()
        registered_consumers = []

        for consumer in consumers:
            registered_consumers.append(consumer_creator(consumer))

    def consume(self, event, *args, **kwargs):
        """
        Consuming the event by applying the consumers registered
        for that event type.
        """
        self.signal.send(event)
