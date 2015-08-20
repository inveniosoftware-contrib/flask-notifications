from flask.ext.notifications.consumers.consumer import Consumer


class LogConsumer(Consumer):
    def __init__(self, filepath="events.log"):
        self.filepath = filepath
        # Permission to read, write and create
        self.default_permissions = "a+w"

    def consume(self, event, *args, **kwargs):
        with open(self.filepath, self.default_permissions) as f:
            f.write(str(event))
