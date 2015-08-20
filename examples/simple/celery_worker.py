#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

# This worker is supposed to register all the tasks and
# execute them within Celery. It is important to execute
# it before the main program.

from app import celery, app, write_to_file
from flask_notifications.event_hub import EventHub

app.app_context().push()
