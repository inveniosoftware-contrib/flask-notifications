# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2015 CERN.
#
# Flask-Notifications is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

import sys

from unittest import TestCase

from flask import Blueprint, Flask, request, url_for

from flask.ext.notifications import NotificationService, current_notifications, notify


class FlaskTestCase(TestCase):
    """
    Mix-in class for creating the Flask application
    """

    def setUp(self):
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.logger.disabled = True
        self.app = app

    def tearDown(self):
        self.app = None


class TestMenu(FlaskTestCase):

    def test_simple_app(self):
        NotificationService(self.app)

        @self.app.route('/test')
        @notify(self.app, '.', 'Test')
        def test():
            return 'test'

        @self.app.route('/level2')
        @notify(self.app, 'level2', 'Level 2')
        def level2():
            return 'level2'

        @self.app.route('/level3')
        @notify(self.app, 'level2.level3', 'Level 3', order=2)
        def level3():
            return 'level3'

        @self.app.route('/level3B')
        @notify(self.app, 'level2.level3B', 'Level 3B', order=1)
        def level3B():
            return 'level3B'

        with self.app.test_client() as c:
            c.get('/test')
            assert request.endpoint == 'test'
            assert current_notifications.url == '/test'
            assert current_notifications.text == 'Test'
            assert current_notifications.active
            self.assertEqual(current_notifications.submenu('level2').text, 'Level 2')
            assert not current_notifications.submenu('level2').active
            assert current_notifications.submenu('missing', auto_create=False) is None
            assert len(current_notifications.list_path('.', '.level2.level3')) == 3
            assert current_notifications.list_path('.', 'missing') is None
            assert current_notifications.list_path('missing', '.level2.level3') is None
            assert current_notifications.list_path('level2.level3B',
                                          'level2.level3') is None

        with self.app.test_client() as c:
            c.get('/level2')
            assert current_notifications.submenu('level2').active

        with self.app.test_client() as c:
            c.get('/level3')
            assert current_notifications.submenu('.level2.level3').active
            assert current_notifications.submenu('level2.level3').active

            assert not current_notifications.has_active_child(recursive=False)
            assert current_notifications.has_active_child()
            assert current_notifications.submenu('level2').has_active_child(
                recursive=False)
            assert current_notifications.submenu('level2').has_active_child()

            item_2 = current_notifications.submenu('level2.level3')
            item_1 = current_notifications.submenu('level2.level3B')
            assert item_1.order < item_2.order
            assert item_1 == current_notifications.submenu('level2').children[0]
            assert item_2 == current_notifications.submenu('level2').children[1]

    # The following test is known to fail on Python 3.4.0 and 3.4.1
    # while it works well on lesser or higher Pythons.  (Additionally
    # cannot use unittest.skipIf() here due to Python-2.6.)
    if sys.version_info != (3, 4, 0, 'final', 0) and \
       sys.version_info != (3, 4, 1, 'final', 0):
        def test_blueprint(self):
            NotificationService(self.app)
            blueprint = Blueprint('foo', 'foo', url_prefix="/foo")

            @self.app.route('/test')
            @notify(self.app, '.', 'Test')
            def test():
                return 'test'

            @blueprint.route('/bar')
            @notify(blueprint, 'bar', 'Foo Bar')
            def bar():
                return 'bar'

            self.app.register_blueprint(blueprint)

            with self.app.test_client() as c:
                c.get('/test')
                assert request.endpoint == 'test'
                assert current_notifications.text == 'Test'

            with self.app.test_client() as c:
                c.get('/foo/bar')
                self.assertEqual(current_notifications.submenu('bar').text, 'Foo Bar')
                self.assertTrue(current_notifications.submenu('bar').active)

    def test_visible_when(self):
        NotificationService(self.app)

        @self.app.route('/always')
        @notify(self.app, 'always', 'Always', visible_when=lambda: True)
        def always():
            return 'never'

        @self.app.route('/never')
        @notify(self.app, 'never', 'Never', visible_when=lambda: False)
        def never():
            return 'never'

        @self.app.route('/normal')
        @notify(self.app, 'normal', 'Normal')
        def normal():
            return 'normal'

        data = {
            'never': {'never': False, 'always': True, 'normal': True},
            'always': {'never': False, 'always': True, 'normal': True},
            'normal': {'never': False, 'always': True, 'normal': True},
        }
        for (k, v) in data.items():
            with self.app.test_client() as c:
                c.get('/' + k)
                for (endpoint, visible) in v.items():
                    self.assertEqual(current_notifications.submenu(endpoint).visible,
                                     visible)

        with self.app.test_request_context():
            current_notifications.submenu('always').hide()

        data = {
            'never': {'never': False, 'always': False, 'normal': True},
            'always': {'never': False, 'always': False, 'normal': True},
            'normal': {'never': False, 'always': False, 'normal': True},
        }
        for (k, v) in data.items():
            with self.app.test_client() as c:
                c.get('/' + k)
                for (endpoint, visible) in v.items():
                    self.assertEqual(current_notifications.submenu(endpoint).visible,
                                     visible)

    def test_active_when(self):
        NotificationService(self.app)

        @self.app.route('/')
        @notify(self.app, 'root', 'Root')
        def root():
            return 'root'

        @self.app.route('/always')
        @notify(self.app, 'always', 'Always', active_when=lambda: True)
        def always():
            return 'always'

        @self.app.route('/never')
        @notify(self.app, 'never', 'Never', active_when=lambda: False)
        def never():
            return 'never'

        @self.app.route('/normal')
        @notify(self.app, 'normal', 'Normal')
        def normal():
            return 'normal'

        data = {
            '/never': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': False
            },
            '/always': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': False
            },
            '/normal': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': True
            },
            '/normal/foo': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': True
            },
            '/bar/normal': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': False
            },
            '/bar/normal/foo': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': False
            },
            '/': {
                'root':   True,
                'never':  False,
                'always': True,
                'normal': False
            },
            '': {
                'root':   True,
                'never':  False,
                'always': True,
                'normal': False
            },
        }
        for (path, testset) in data.items():
            with self.app.test_client() as c:
                c.get(path)
                for (endpoint, active_should) in testset.items():
                    active_is = current_notifications.submenu(endpoint).active
                    self.assertEqual(
                        active_is,
                        active_should,
                        'path="{0}" submenu_by_endpoint="{1}" '
                        'active_is={2} active_should={3}'.format(
                            path,
                            endpoint,
                            active_is,
                            active_should
                        )
                    )

    def test_dynamic_url(self):
        NotificationService(self.app)

        @self.app.route('/<int:id>/<string:name>')
        @notify(self.app, 'test', 'Test',
                       endpoint_arguments_constructor=lambda: {
                           'event_id': request.view_args['event_id'],
                           'name': request.view_args['name'],
                           })
        def test(id, name):
            return str(id) + ':' + name

        with self.app.test_request_context():
            url = url_for('test', id=1, name='foo')

        with self.app.test_client() as c:
            c.get(url)
            assert url == current_notifications.submenu('test').url
            assert current_notifications.submenu('missing').url == '#'

    def test_kwargs(self):
        """Test optional arguments."""
        NotificationService(self.app)
        count = 5

        @self.app.route('/test')
        @notify(self.app, 'test', 'Test', count=count)
        def test():
            return 'count'

        with self.app.test_client() as c:
            c.get('/test')
            assert count == current_notifications.submenu('test').count

    def test_kwargs_override(self):
        """Test if optional arguments cannot be overriden."""
        NotificationService(self.app)

        @self.app.route('/test')
        @notify(self.app, 'test', 'Test', url='/test')
        def test():
            pass

        with self.app.test_client() as c:
            self.assertRaises(RuntimeError, c.get, '/test')
