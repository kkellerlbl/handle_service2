# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
import inspect
import copy

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
        cls.user_id = auth_client.get_user(token)

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

    def test_persist_handle_fail(self):
        self.start_test()
        handler = self.getHandler()

        with self.assertRaises(ValueError) as context:
            handle = {'missing_id': 'id'}
            handler.persist_handle(handle, self.user_id)

        self.assertIn('Missing one or more required positional field', str(context.exception.args))

        with self.assertRaises(ValueError) as context:
            handle = {'id': ''}
            handler.persist_handle(handle, self.user_id)

        self.assertIn('Missing one or more required positional field', str(context.exception.args))

        with self.assertRaises(ValueError) as context:
            handle = {'file_name': None}
            handler.persist_handle(handle, self.user_id)

        self.assertIn('Missing one or more required positional field', str(context.exception.args))

    def test_persist_handle_okay(self):
        self.start_test()
        handler = self.getHandler()

        handle = {'id': 'id',
                  'file_name': 'file_name',
                  'type': 'shock',
                  'url': 'http://ci.kbase.us:7044/'}
        # testing persist_handle with non-existing handle (inserting a handle)
        hid = handler.persist_handle(handle, self.user_id)
        handles = handler.fetch_handles_by({'elements': [hid], 'field_name': 'hid'})
        self.assertEqual(len(handles), 1)
        handle = handles[0]
        self.assertEqual(handle.get('hid'), hid)
        self.assertEqual(handle.get('id'), 'id')
        self.assertEqual(handle.get('file_name'), 'file_name')
        self.assertEqual(handle.get('created_by'), self.user_id)

        # testing persist_handle with existing handle (updating a handle)
        new_handle = copy.deepcopy(handle)
        new_file_name = 'new_file_name'
        new_id = 'new_id'
        new_handle['file_name'] = new_file_name
        new_handle['id'] = new_id
        new_hid = handler.persist_handle(new_handle, self.user_id)
        handles = handler.fetch_handles_by({'elements': [new_hid], 'field_name': 'hid'})
        self.assertEqual(len(handles), 1)
        handle = handles[0]
        self.assertEqual(handle.get('hid'), hid)
        self.assertEqual(handle.get('id'), new_id)
        self.assertEqual(handle.get('file_name'), new_file_name)
        self.assertEqual(handle.get('created_by'), self.user_id)

        self.assertEqual(new_hid, hid)
