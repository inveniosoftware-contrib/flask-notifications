#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

from flask.ext.email import EmailMessage, SMTPMail

from flask.ext.notifications.consumers.email.email_dependency import EmailDependency


class FlaskEmailDependency(EmailDependency):
    def __init__(self, mail, sender, recipients):
        """
        :param mail: This object represents the Flask-Email mailbox
        """
        super(FlaskEmailDependency, self).__init__(mail, sender, recipients)

    @classmethod
    def from_app(cls, app, sender=None, recipients=None):
        """
        This method only returns a new instance because Flask-Email does not register itself
        to the extensions array in the app. The backend created is SmtpMail by default.
        :param app:
        :return:
        """
        mail = SMTPMail(app, fail_silently=False)
        return cls(mail, sender, recipients)

    def create_message(self, event):
        return EmailMessage("Event {0}".format(event.event_id),
                            str(event),
                            self.sender,
                            self.recipients)

    def send_function(self):
        def flaskemail_send(event):
            with self.mail.app.app_context():
                email = self.create_message(event)
                email.send(self.mail)
                print(str(email))

        return flaskemail_send
