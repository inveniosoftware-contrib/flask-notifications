from flask.ext.notifications.consumers.consumer import Consumer


class LogConsumer(Consumer):
    def __init__(self):
        self.default_filename = "events.log"
        self.default_permissions = "a+w"

    def consume(self, event, *args, **kwargs):
        f = open(self.default_filename, self.default_permissions)
        f.write(str(event))
