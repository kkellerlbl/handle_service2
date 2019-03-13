# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
import inspect

from AbstractHandle.authclient import KBaseAuth as _KBaseAuth

from mongo_util import MongoHelper
from AbstractHandle.Utils.Handler import Handler


class HandlerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('AbstractHandle'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.cfg['KB_AUTH_TOKEN'] = token
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)

        cls.mongo_helper = MongoHelper()
        cls.my_client = cls.mongo_helper.create_test_db(db=cls.cfg['mongo-database'],
                                                        col=cls.cfg['mongo-collection'])
        cls.handler = Handler(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getHandler(self):
        return self.__class__.handler

    def start_test(self):
        testname = inspect.stack()[1][3]
        print('\n*** starting test: ' + testname + ' **')

    def test_init_ok(self):
        self.start_test()
        class_attri = ['token', 'mongo_util']
        handler = self.getHandler()
        self.assertTrue(set(class_attri) <= set(handler.__dict__.keys()))

    def test_fetch_handles_by_fail(self):
        self.start_test()
        handler = self.getHandler()

        with self.assertRaises(ValueError) as context:
            handler.fetch_handles_by({'missing_element': 'element', 'field_name': 'field_name'})

        self.assertIn('Required keys', str(context.exception.args))

        with self.assertRaises(ValueError) as context:
            handler.fetch_handles_by({'element': 'element', 'missing_field_name': 'field_name'})

        self.assertIn('Required keys', str(context.exception.args))

    def test_fetch_handles_by_okay(self):
        self.start_test()
        handler = self.getHandler()

        # test query 'hid' field
        elements = [68021, 68022]
        field_name = 'hid'
        handles = handler.fetch_handles_by({'elements': elements, 'field_name': field_name})
        self.assertEqual(len(handles), 2)
        self.assertCountEqual(elements, [h.get('hid') for h in handles])

        # test query 'hid' field with empty data
        elements = [0]
        field_name = 'hid'
        handles = handler.fetch_handles_by({'elements': elements, 'field_name': field_name})
        self.assertEqual(len(handles), 0)

        # test query 'id' field
        elements = ['b753774f-0bbd-4b96-9202-89b0c70bf31c']
        field_name = 'id'
        handles = handler.fetch_handles_by({'elements': elements, 'field_name': field_name})
        self.assertEqual(len(handles), 1)
        handle = handles[0]
        self.assertFalse('_id' in handle)
        self.assertEqual(handle.get('hid'), 67712)
