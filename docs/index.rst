====================
 Flask-Notifications
====================
.. currentmodule:: flask_notifications

Flask-Notifications is a Flask extension that provides generic notification
framework.

Contents
--------

.. contents::
   :local:
   :depth: 1
   :backlinks: none


.. _installation:

Installation
============

Flask-Notifications is on PyPI so all you need is:

.. code-block:: console

    $ pip install Flask-Notifications

The development version can be downloaded from `its page at GitHub
<http://github.com/inveniosoftware/flask-menu>`_.

.. code-block:: console

    $ git clone https://github.com/inveniosoftware/flask-menu.git
    $ cd flask-menu
    $ python setup.py develop
    $ ./run-tests.sh

Requirements
^^^^^^^^^^^^

Flask-Notifications has the following dependencies:

* `Flask <https://pypi.python.org/pypi/Flask>`_
* `six <https://pypi.python.org/pypi/six>`_

Flask-Notifications requires Python version 2.6, 2.7 or 3.3+.


.. _usage:

Usage
=====

This guide assumes that you have successfully installed ``Flask-Notifications``
package already.  If not, please follow the :ref:`installation`
instructions first.

Simple Example
^^^^^^^^^^^^^^

Here is a simple Flask-Notifications usage example:

.. code-block:: python

    from flask import Flask
    from flask import render_template_string
    from flask_notifications import Menu, register_menu

    app = Flask(__name__)
    Menu(app=app)

    def tmpl_show_menu():
        return render_template_string(
            """
            {%- for item in current_menu.children %}
                {% if item.active %}*{% endif %}{{ item.text }}
            {% endfor -%}
            """)

    @app.route('/')
    @register_menu(app, '.', 'Home')
    def index():
        return tmpl_show_menu()

    @app.route('/first')
    @register_menu(app, '.first', 'First', order=0)
    def first():
        return tmpl_show_menu()

    @app.route('/second')
    @register_menu(app, '.second', 'Second', order=1)
    def second():
        return tmpl_show_menu()

    if __name__ == '__main__':
        app.run(debug=True)

If you save the above as ``app.py``, you can run the example
application using your Python interpreter:

.. code-block:: console

    $ python app.py
     * Running on http://127.0.0.1:5000/

and you can observe generated menu on the example pages:

.. code-block:: console

    $ firefox http://127.0.0.1:5000/
    $ firefox http://127.0.0.1:5000/first
    $ firefox http://127.0.0.1:5000/second

You should now be able to emulate this example in your own Flask
applications.  For more information, please read the :ref:`templating`
guide, the :ref:`blueprints` guide, and peruse the :ref:`api`.


.. _templating:

Templating
==========

By default, a proxy object to `current_menu` is added to your Jinja2
context as `current_menu` to help you with creating navigation bar.
For example:

.. code-block:: jinja

    <ul>
      {%- for item in current_menu.children recursive -%}
      <li>
        <a href="{{ item.url}}">{{ item.text }}</a>
        {%- if item.children -%}
        <ul>
          {{ loop(item.children) }}
        </ul>
        {%- endif -%}
      </li>
      {%- endfor -%}
    </ul>

.. _blueprints:

Blueprint Support
=================

The most import part of an modular Flask application is Blueprint. You
can create one for your application somewhere in your code and decorate
your view function, like this:

.. code-block:: python

    from flask import Blueprint
    from flask_notifications import register_menu

    bp_account = Blueprint('account', __name__, url_prefix='/account')

    @bp_account.route('/')
    @register_menu(bp_account, '.account', 'Your account')
    def index():
        pass


Sometimes you want to combine multiple blueprints and organize the
navigation to certain hierarchy.

.. code-block:: python

    from flask import Blueprint
    from flask_notifications import register_menu

    bp_social = Blueprint('social', __name__, url_prefix='/social')

    @bp_account.route('/list')
    @register_menu(bp_social, '.account.list', 'Social networks')
    def list():
        pass

As a result of this, your `current_menu` object will contain a list
with 3 items while processing a request for `/social/list`.

.. code-block:: python

    >>> from example import app
    >>> from flask_notifications import current_menu
    >>> import account
    >>> import social
    >>> app.register_blueprint(account.bp_account)
    >>> app.register_blueprint(social.bp_social)
    >>> with app.test_client() as c:
    ...     c.get('/social/list')
    ...     assert current_menu.submenu('account.list').active
    ...     current_menu.children


Flask-Classy
============

Flask-Classy is a library commonly used in Flask development and gives 
additional structure to apps which already make use of blueprints as
well as apps which do not use blueprints. 

Using Flask-Notifications with Flask-Classy is rather simple:

.. code-block:: python

    from flask_classy import FlaskView
    from flask_notifications import classy_menu_item

    class MyEndpoint(FlaskView):
        route_base = '/'

        @classy_menu_item('frontend.account', 'Home', order=0)
        def index(self):
            # Do something.
            pass


Instead of using the `@menu.register_menu` decorator, we use classy_menu_item. 
All usage is otherwise the same to `register_menu`, however you do not need 
to provide reference to the blueprint/app.

You do have to register the entire class with flask-menu at runtime however.

.. code-block:: python


    from MyEndpoint import MyEndpoint
    from flask import Blueprint
    from flask_notifications import register_flaskview

    bp = Blueprint('bp', __name__)

    MyEndpoint.register(bp)
    register_flaskview(bp, MyEndpoint)

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


.. include:: ../CHANGES

.. include:: ../CONTRIBUTING.rst

License
=======

.. include:: ../LICENSE

.. include:: ../AUTHORS
