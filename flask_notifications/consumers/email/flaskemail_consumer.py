# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Email consumer using the Flask-Mail extension."""

from flask.ext.email import EmailMessage, SMTPMail
from flask_notifications.event import Event
from flask_notifications.consumers.email.email_consumer import EmailConsumer


class FlaskEmailConsumer(EmailConsumer):

    """Send an email using the Flask-Email extension."""

    def __init__(self, mail, sender=None, recipients=[]):
        """Initialize Flask-Email extension.

        :param mail: This object represents the Flask-Email mailbox
        """
        super(FlaskEmailConsumer, self).__init__(
            mail, sender, recipients
        )

    @classmethod
    def from_app(cls, app, sender=None, recipients=[]):
        """Return a new instance of SMTP using Flask-Email always.

        Flask-Email does not register itself to the extensions
        array in the app. The backend created is SmtpMail by default.
        """
        mail = SMTPMail(app, fail_silently=False)
        return cls(mail, sender, recipients)

    def create_message(self, event_json):
        """Create a message from an event."""
        event = Event.from_json(event_json)
        return EmailMessage(
            "Event {0}".format(event['event_id']),
            event_json, self.sender, self.recipients
        )

    def consume(self, event_json, *args, **kwargs):
        """Consume an event sending it as an email."""
        email = self.create_message(event_json)
        return email.send(self.mail)
