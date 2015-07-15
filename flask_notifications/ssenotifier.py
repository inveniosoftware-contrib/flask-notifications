from sse import Sse


class SseNotifier(object):
    def __init__(self, pubsub):
        self.pubsub = pubsub
        self.sse = Sse()

    def __iter__(self):
        self.pubsub.subscribe("test")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                self.sse.add_message("", message['data'])
                for data in self.sse:
                    yield data.encode('u8')
