# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Declaration of a generic EmailConsumer."""

import abc
from flask_notifications.consumers.consumer import Consumer


class EmailConsumer(Consumer):

    """Base class of an Email consumer."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, mail, sender=None, recipients=[]):
        """Initialize of the email dependency, which inherits Consumer.

        :param mail: Instance of the extension already initialized with app
        :param sender: Who is sending the notification
        :param recipients: Addresses that will receive a notification
        """
        self.mail = mail
        self.sender = sender
        self.recipients = recipients

    @classmethod
    @abc.abstractmethod
    def from_app(cls, app):
        """Use or create an email extension.

        :param app: Application to wrap up new mail extension or get
                    the existing one
        """

    @abc.abstractmethod
    def create_message(self, event_json):
        """Create the email that will be sent.

        If you want to custom the notification that your user
        will receive from an event, extend and override this method.
        """
