#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.


class Consumers(object):
    def __init__(self, celery, redis, email_dependency):
        self.celery = celery
        self.redis = redis
        self.send_email_from_event = email_dependency.send_function()

        self.__default_filename = "events.log"
        self.__default_permission = "a+"

        # Adding all the internal functions that actually are tasks (both async and sync)
        self.all = [self.email(), self.log(), self.push()]

    def email(self):
        """
        :return: Asynchronous task that send an email using Flask-Mail (SMTP)
        and a default gmail account.
        """

        @self.celery.task()
        def send_email(event):
            self.send_email_from_event(event)

        return send_email.delay

    def log(self):
        """
        :return: Asynchronous task that logs to a file the different events.
        """

        @self.celery.task()
        def write_to_file(event):
            f = open(self.__default_filename, self.__default_permission)
            f.write(str(event))

        return write_to_file.delay

    def push(self):
        """
        This is not an asynchronous task because it would block the connection
        with Redis and the notification would never be sent. Also, it is a
        lightweight and fast task.

        :return: Synchronous function that push a notification to a channel
        """

        def push(event):
            self.redis.publish("test", str(event))

        return push
