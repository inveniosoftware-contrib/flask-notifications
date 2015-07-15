from flask.ext.mail import Message


class Consumers(object):
    def __init__(self, mail, celery, redis):
        self.mail = mail
        self.celery = celery
        self.redis = redis
        self.__default_filename = "events.log"
        self.__default_permission = "w+"
        self.__default_email_account = "invnotifications@gmail.com"

        # Adding all the internal functions that actually are tasks (both async and sync)
        self.all = [self.email(), self.log(), self.push()]

    def email(self):
        """
        :return: Asynchronous task that send an email using Flask-Mail (SMTP)
        and a default gmail account.
        """
        @self.celery.task()
        def send_email(event):
            message = Message(subject="Event {0}".format(event.event_id),
                              sender=self.__default_email_account,
                              recipients=[self.__default_email_account],
                              body=str(event))
            self.mail.send(message)

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
            self.redis.publish("test", "This is a test")

        return push
