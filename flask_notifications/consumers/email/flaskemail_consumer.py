#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.
from flask.ext.email import EmailMessage, SMTPMail
from flask_notifications.consumers.email.email_consumer import EmailConsumer


class FlaskEmailConsumer(EmailConsumer):
    def __init__(self, mail, sender, recipients):
        """
        Email consumer that uses the FlaskEmail module
        :param mail: This object represents the Flask-Email
        mailbox
        """

        super(FlaskEmailConsumer, self).__init__(
            mail, sender, recipients
        )

    @classmethod
    def from_app(cls, app, sender=None, recipients=None):
        """
        This method only returns a new instance because
        Flask-Email does not register itself to the extensions
        array in the app. The backend created is SmtpMail by default.
        :param app:
        :return:
        """
        mail = SMTPMail(app, fail_silently=False)
        return cls(mail, sender, recipients)

    def create_message(self, event):
        return EmailMessage(
            "Event {0}".format(event.event_id),
            str(event), self.sender, self.recipients
        )

    def consume(self, event, *args, **kwargs):
        with self.mail.app.app_context():
            email = self.create_message(event)
            return email.send(self.mail)
