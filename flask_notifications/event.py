from flask.json import JSONEncoder, JSONDecoder, loads


class Event(object):
    """
    This class models an event (notification) used to signal to the API which behaviour
    should adopt.
    The arguments passed are the event type, the body of the notification and the validity,
    which is a datetime.
    """

    def __init__(self, event_id, title, body):
        self.event_id = event_id
        self.title = title
        self.body = body

    @classmethod
    def from_json(cls, json):
        event = cls.dict_to_event(cls.json_to_dict(json))
        return event

    @staticmethod
    def json_to_dict(json):
        event = loads(json)
        return event

    @staticmethod
    def dict_to_event(d):
        event = None
        if "event_id" in d and "title" in d and "body" in d:
            event = Event(d["event_id"], d["title"], d["body"])
        return event

    def __str__(self):
        return "Event {0}({1}): {2}".format(self.event_id, self.title, self.body)


class ExtendedJSONEncoder(JSONEncoder):
    """This JSON encoder serialize the class Event into a specified JSON format following his signature."""

    def default(self, o):
        if isinstance(o, Event):
            return {
                "event_id": o.event_id,
                "title": o.title,
                "body": o.body,
            }
        return JSONEncoder.default(self, o)


class ExtendedJSONDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.multiple_dict_to_obj)

    @staticmethod
    def multiple_dict_to_obj(d):
        event = Event.dict_to_event(d)
        return event if event is not None else d
