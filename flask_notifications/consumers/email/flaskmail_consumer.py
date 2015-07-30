#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.
import celery

from flask.ext.mail import Mail, Message

from flask.ext.notifications.consumers.email.email_consumer import EmailConsumer


class FlaskMailConsumer(EmailConsumer):
    def __init__(self, mail, sender=None, recipients=None):
        super(FlaskMailConsumer, self).__init__(
            mail, sender, recipients
        )

    @classmethod
    def from_app(cls, app, sender=None, recipients=None):
        mail = Mail(app) if 'mail' not in app.extensions else \
            app.extensions['mail']
        return cls(mail, sender, recipients)

    def create_message(self, event):
        return Message(subject="Event {0}".format(event.event_id),
                       sender=self.sender,
                       recipients=self.recipients,
                       body=str(event))

    def consume(self, event, *args, **kwargs):
        with self.mail.app.app_context():
            message = self.create_message(event)
            self.mail.send(message)
