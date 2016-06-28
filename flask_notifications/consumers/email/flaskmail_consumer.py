# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015, 2016 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Email consumer using the Flask Mail extension."""

from flask.ext.mail import Mail, Message

from flask_notifications.event import Event
from flask_notifications.consumers.email.email_consumer import EmailConsumer


class FlaskMailConsumer(EmailConsumer):
    """Send an email using the Flask-Mail extension."""

    def __init__(self, mail, sender=None, recipients=[]):
        """Initialise FlaskMail app."""
        super(FlaskMailConsumer, self).__init__(
            mail, sender, recipients
        )

    @classmethod
    def from_app(cls, app, sender=None, recipients=[]):
        """Get or create mail extension from app."""
        mail = Mail(app) if 'mail' not in app.extensions else \
            app.extensions['mail']
        return cls(mail, sender, recipients)

    def create_message(self, event_json):
        """Create a message from an event."""
        event = Event.from_json(event_json)
        return Message(subject="Event {0}".format(event["event_id"]),
                       sender=self.sender,
                       recipients=self.recipients,
                       body=event_json)

    def consume(self, event_json, *args, **kwargs):
        """Consume an event sending it as an email."""
        message = self.create_message(event_json)
        self.mail.send(message)
