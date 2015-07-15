from app import celery, app
from flask.ext.notifications import consumers

app.app_context().push()