e = Event(id = 1,
          title = "New Message from @jim",
          body = "Hey! When do we meet?")

notification_system = NotificationService(
    flask_app=app,
    config=config
)

notification_system.send(event)