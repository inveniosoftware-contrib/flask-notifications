# -*- coding: utf-8 -*-
#
# This file is part of Flask-Notifications
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

====================
 Flask-Notifications
====================
.. currentmodule:: flask_notifications

Flask-Notifications is a Flask extension that provides a generic real-time
notification framework. 

Contents
--------

.. contents::
   :local:
   :depth: 2
   :backlinks: none


.. _installation:

Installation
============

Flask-Notifications is on PyPI so all you need is:

.. code-block:: console

    $ pip install Flask-Notifications

The development version can be downloaded from `its page at GitHub
<http://github.com/inveniosoftware/flask-notifications>`_.

.. code-block:: console

    $ git clone https://github.com/inveniosoftware/flask-notifications.git
    $ cd flask-notifications
    $ python setup.py develop
    $ ./run-tests.sh

Requirements
^^^^^^^^^^^^

Flask-Notifications has the following dependencies:

* `Flask <https://pypi.python.org/pypi/Flask>`_
* `Flask-CeleryExt <https://pypi.python.org/pypi/Flask-CeleryExt/0.1.0>`_
* `Redis <https://pypi.python.org/pypi/redis/>`_
* `Gevent <https://pypi.python.org/pypi/gevent/1.1b3>`_
* `Blinker <https://pypi.python.org/pypi/blinker/1.4>`_
* `Sse <https://pypi.python.org/pypi/sse/1.2>`_
* `six <https://pypi.python.org/pypi/six>`_

Flask-Notifications requires Python version 2.6, 2.7 or 3.3+.


.. _usage:

Usage
=====

This guide assumes that you have successfully installed ``Flask-Notifications``
package already.  If not, please follow the :ref:`installation`
instructions first.

Building a simple notification system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``Flask-Notifications`` provides a simple API to build your own real-time
notification system. In this guide, we will see how to build such a system
easily in a few steps.

First, we create the ``Flask`` application and initialise the Notifications
extension. ``Flask-Notifications`` depends upon Celery and Redis. The first
one is used for task processing and the second one for the Pub/Sub primitives.
Then, we reuse Redis as a broker too.

In case you want to use another broker as *RabbitMQ*, you can implement the
Pub/Sub or Fan-Out pattern by yourself by extending the ``Backend`` type.

.. code-block:: python

    from flask import Flask
    from flask_notifications import Notifications

    app = Flask(__name__)
    notifications = Notifications(app=app)


or:

.. code-block:: python

    from flask import Flask
    from flask_notifications import Notifications

    app = Flask(__name__)
    notifications = Notifications()
    notifications.init_app(app=app)

or:

.. code-block:: python

    from flask import Flask
    from flask_notifications import Notifications

    # Corresponding information for brokers and Celery
    config = {...}
    celery = FlaskCeleryExt(app).celery
    redis = StrictRedis(host=redis_host)

    app = Flask(__name__)
    notifications = Notifications()
    notifications.init_app(app=app, celery=celery, broker=redis)

Now, we create a ``EventHub``. A hub is composed of a filter and a list of consumers.
When an event is sent to the hub, the filter is applied to that event. If it
passes, it is sent to all the registered consumers.

An ``EventHub`` requires a label as a parameter. This label cannot be randomized.
In order to make a reference to a hub, one should get first his identifier, which
is not the same as the label.

.. code-block:: python

    test_hub = notifications.create_hub("TestHub")
    test_hub_id = user_hub.hub_id


The next step is to set up our hub. Let's say we want to aggregate in that hub
all the events with the "test" type and which are sent from now on.

.. code-block:: python

    import datetime
    now = datetime.now()

    from flask_notifications.filters.with_event_type import WithEventType
    from flask_notifications.filters.before_date import BeforeDate

    event_hub.filter_by(
        WithEventType("test") & Not(BeforeDate(now))
    )


This creates a composed filter with those requirements. Any ``EventFilter`` can
be composed using the bitwise operators (``&``, ``|`` and ``^``) -it's not possible to use 
the logical operators ``and``, ``or`` and ``xor`` because Python2.7 does not allow to
override his behaviour-.

Now, we register some consumers to our hub.

.. code-block:: python

    @event_hub.register_consumer(celery_task_name="app.write_to_file")
    def write_to_file(event, *args, **kwargs):
        with open("events.log", "a+w") as f:
            f.write(str(event))


    push_consumer = PushConsumer(redis, event_hub_id)
    event_hub.register_consumer(push_consumer)

When registering a function using the decorator, it is very important to specify
the ``celery_task_name`` relatively to your application to help the workers to 
detect the function. More information `here <http://celery.readthedocs.io/en/latest/userguide/tasks.html#names>`_.

If you feel like to write a complex consumer, you can extend the the ``Consumer``
interface. Also, this interface has some hooks. One before consuming the event
and the other after. This is very handy when you want to confirm that an event
has been stored and hence send it to a database to persist it.

The only missing step is to send notifications.

.. code-block:: python

    event = Event(None, "test", "This event will pass the filter",
                  "This is the body of the test", sender="system")
    notifications.send(event.to_json())

    event = Event(None, "system", "This event will not pass the filter",
                  "This is the body of the test", sender="system")
    notifications.send(event.to_json())


``Event`` is a dictionary with a predefined model. If you would like to
add your own fields and filter them, you just need to add the field to
the ``Event`` and create a new filter by extending ``EventFilter``.

You should now be able to emulate this example in your own Flask
applications.  For more information, please read the :ref:`architecture`
guide, check the :ref:`predefined consumers` section, the :ref:`config`
and peruse the :ref:`api`.

.. _architecture:

Architecture
============
The application is composed of two main parts: the main program and the
workers. These workers will process asynchronously all the consumers
in the hubs.

As we are defining functions using the ``@register_consumer`` decorator,
the workers need to know and register this function as well. Therefore, a worker
imports the main program and compiles it. It is very important not to have
any randomized value because they won't match neither in the main application
nor the program.

*If you are going to use predefined consumers, you need to add the necessary
configuration values to the Flask configuration.*

.. _config:

Configuration
=============
``Flask-Notifications`` only needs one parameter in the Flask configuration: **BACKEND**.
This option points to the Python path of a subclass of ``Backend``. By default,
it uses ``RedisBackend``, but you can add your own implementation of ``Backend``
using other brokers like RabbitMQ. You just need to make you sure that the option
has the right path to the class in order to be imported by the Notifications module.

.. code-block:: python

    config = {
        ...,
        # Default option
        "BACKEND": "flask_notifications.pubsub.redis_pubsub.RedisPubSub",
    }

Also, ``Flask-Notifications`` uses the **JSON** serializer and deserializer to
pass the events to the consumers. So, it is important that you allow the json
serializer in the Celery configuration by using the following options (you can
add any serializer that you want, the important thing is to enable the json
serializer):

.. code-block:: python

    config = {
        ...,
        "CELERY_ACCEPT_CONTENT": ["application/json"],
        "CELERY_TASK_SERIALIZER": "json",
        "CELERY_RESULT_SERIALIZER": "json",
    }


.. _predefined consumers:

Predefined Consumers
====================
The predefined consumers exist to fulfil simple needs like sending an email or
writing a log. You can use them in your code by importing and registering them.

For more complex consumers, you may create your own by extending a predefined
consumer or creating a new one extending ``Consumer``.

Current predefined consumers:

.. module:: flask_notifications.consumers.push_consumer

.. class:: push_consumer.PushConsumer

.. class:: log_consumer.LogConsumer

.. class:: flaskemail_consumer.FlaskEmailConsumer

.. class:: flaskmail_consumer.FlaskMailConsumer

.. _api:

API
===

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

Flask extension
^^^^^^^^^^^^^^^

.. module:: flask_notifications

.. autoclass:: Notifications
   :members:

.. autoclass:: EventHub
   :members:

.. module:: flask_notifications.event

.. autoclass:: Event
   :members:

.. module:: flask_notifications.event_filter

.. autoclass:: EventFilter
   :members:

.. module:: flask_notifications.consumers.consumer

.. autoclass:: Consumer
   :members:

Decorators
^^^^^^^^^^

.. module:: flask_notifications.event_hub

.. function:: register_consumer

Proxies
^^^^^^^^^^

.. data:: current_notifications
   Root of the notification extension.


.. include:: ../CHANGES

.. include:: ../CONTRIBUTING.rst

License
=======

.. include:: ../LICENSE

.. include:: ../AUTHORS
