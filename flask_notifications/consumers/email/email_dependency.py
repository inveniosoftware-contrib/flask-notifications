#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

import abc


class EmailDependency(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, mail, sender=None, recipients=None):
        """
        Initializer of the email dependency
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
        """
        If a mail extension has been already initialised, use that one. Otherwise,
        initialise one.
        :param app: Application to wrap up new mail extension or get the existing one
        :return: Instance of FlaskMailDependency
        """

    @abc.abstractmethod
    def create_message(self, event):
        """
        This method creates the message (email) that will be sent with the send_function.
        If you want to custom the notification that your user will receive from an event,
        extend and override this method.
        """

    @abc.abstractmethod
    def send_function(self):
        """
        It is important that the returning function does not have any self
        parameter, that is the reason we create the function inside this one and
        return that function, which only accepts an event as a parameter.
        :return: Function that sends an email
        """
