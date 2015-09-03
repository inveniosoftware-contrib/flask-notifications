# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""EventHub declaration."""

from six import callable
from blinker import signal
from six import wraps

from flask_notifications.filters.always import Always


class EventHub:

    """An EventHub is composed of a filter and consumers."""

    def __init__(self, hub_alias, celery):
        """Init the Hub with a hub alias and a Celery instance."""
        self.hub_id = "event-hub-{0}".format(hub_alias)
        self.signal = signal(self.hub_id)

        self._hub_event_filter = Always()
        self.celery = celery

        # To confirm registration, async consumer != consumer
        self.registered_consumers = {}

    def register_consumer(self, f=None, **kwargs):
        """Register a function making it asynchronous.

        The consumer is converted to async using the task decorator
        with the weak option enabled because the function is created in scope.
        """
        def register_async_consumer(f):
            @wraps(f)
            def make_async():
                maker = self.celery.task(**kwargs)
                return maker(f)

            async_f = make_async()

            def apply_with_expiration_check(event):
                print(str(event["expiration_datetime"]))
                return async_f.apply_async(
                    (event.to_json(),),
                    expires=event["expiration_datetime"]
                )

            if not self.is_registered(f):
                self.signal.connect(apply_with_expiration_check, weak=False)
                self.registered_consumers[f] = async_f
            return f

        if f and callable(f):
            return register_async_consumer(f)
        else:
            return register_async_consumer

    def is_registered(self, consumer_or_name):
        """Check if a consumer is registered."""
        return consumer_or_name in self.registered_consumers

    def deregister_consumer(self, consumer):
        """Deregister one or more consumers."""
        async_consumer = self.registered_consumers[consumer]
        self.signal.disconnect(async_consumer)
        try:
            del self.registered_consumers[consumer]
        except KeyError:
            pass

    def filter_by(self, event_filter):
        """Filter the events to know if the event should be processed."""
        self._hub_event_filter = event_filter

    def consume(self, event, *args, **kwargs):
        """Consume the event by all the consumers."""
        if self._hub_event_filter(event):
            self.signal.send(event)
