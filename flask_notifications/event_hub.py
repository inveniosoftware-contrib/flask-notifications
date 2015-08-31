#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from blinker import signal

from flask_notifications.filters.always import Always


class EventHub:

    "An EventHub is composed of a filter and consumers."

    def __init__(self, hub_alias, celery):
        """Init the Hub with a the name of the hub and an instance
        of Celery to perform async execution in the consumers.
        """
        self.hub_id = "event-hub-{}".format(hub_alias)
        self.signal = signal(self.hub_id)

        self._hub_event_filter = Always()
        self.celery = celery

        # We need to keep track of them to disconnect them from a signal
        # Async consumer != consumer
        self.registered_consumers = {}

    def consumer(self, celery_task_name=None):
        """Decorator that modifies the given function, register it
        making it asynchronous and connect the function to the signal.
        """
        def _make_async(f):
            async_creator = self.celery.task(name=celery_task_name)
            return async_creator(f)

        def register_async_consumer(f):
            # Weak is False because the receiver attached is created
            # in scope and there is no external reference to it
            async_f = _make_async(f)
            self.signal.connect(async_f.delay, weak=False)
            self.registered_consumers[f.__name__] = async_f

            return async_f

        return register_async_consumer

    def is_registered(self, consumer_to_check):
        """Check if a consumer is registered."""
        return consumer_to_check.__name__ in self.registered_consumers

    def register_consumer(self, consumer):
        """Register one consumer wrapping it in an asynchronous execution."""
        if not self.is_registered(consumer):
            register_as_async = self.consumer()
            register_as_async(consumer)

    def register_consumers(self, consumers_iterable):
        """Register sequence of consumers."""
        for consumer in consumers_iterable:
            self.register_consumer(consumer)

    def deregister_consumer(self, consumer):
        """Deregister a consumer in order to not execute it anymore."""
        async_consumer = self.registered_consumers[consumer.__name__]
        self.signal.disconnect(async_consumer)
        del self.registered_consumers[consumer.__name__]

    def deregister_consumers(self, consumers):
        """Remove consumers from the register."""
        for consumer in consumers:
            self.deregister_consumer(consumer)

    def filter_by(self, event_filter):
        """Filter the events by the following filter. The filter
        can be composed from other filters or only one.
        """
        self._hub_event_filter = event_filter

    def consume(self, event, *args, **kwargs):
        """Consuming the event by applying the consumers registered
        for that event type.
        """
        if self._hub_event_filter(event):
            self.signal.send(event.to_json())
