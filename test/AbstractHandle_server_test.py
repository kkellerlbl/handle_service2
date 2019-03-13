# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
import inspect

from AbstractHandle.AbstractHandleImpl import AbstractHandle
from AbstractHandle.AbstractHandleServer import MethodContext
from AbstractHandle.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace

from sql_util import SQLHelper
from mongo_util import MongoHelper


class handle_serviceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('AbstractHandle'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'AbstractHandle',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = AbstractHandle(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.sql_helper = SQLHelper()
        cls.mongo_helper = MongoHelper()
        cls.my_client = cls.mongo_helper.create_test_db(db=cls.cfg['mongo-database'],
                                                        col=cls.cfg['mongo-collection'])

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_AbstractHandle_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def createMongoDB(self):
        if hasattr(self.__class__, 'my_client'):
            return self.__class__.my_client

        my_client = self.mongo_helper.create_test_db()

        self.__class__.my_client = my_client
        return my_client

    def start_test(self):
        testname = inspect.stack()[1][3]
        print('\n*** starting test: ' + testname + ' **')

    def test_fetch_handles_by_okay(self):
        self.start_test()
        handler = self.getImpl()

        # test query 'hid' field
        elements = [68021, 68022]
        field_name = 'hid'
        handles = handler.fetch_handles_by(self.ctx, {'elements': elements, 'field_name': field_name})[0]
        self.assertEqual(len(handles), 2)
        self.assertCountEqual(elements, [h.get('hid') for h in handles])

        # test query 'hid' field with empty data
        elements = [0]
        field_name = 'hid'
        handles = handler.fetch_handles_by(self.ctx, {'elements': elements, 'field_name': field_name})[0]
        self.assertEqual(len(handles), 0)

        # test query 'id' field
        elements = ['b753774f-0bbd-4b96-9202-89b0c70bf31c']
        field_name = 'id'
        handles = handler.fetch_handles_by(self.ctx, {'elements': elements, 'field_name': field_name})[0]
        self.assertEqual(len(handles), 1)
        handle = handles[0]
        self.assertFalse('_id' in handle)
        self.assertEqual(handle.get('hid'), 67712)

    def test_ids_to_handles_okay(self):
        self.start_test()
        handler = self.getImpl()

        ids = ['b753774f-0bbd-4b96-9202-89b0c70bf31c']
        handles = handler.ids_to_handles(self.ctx, ids)[0]
        self.assertEqual(len(handles), 1)
        handle = handles[0]
        self.assertFalse('_id' in handle)
        self.assertEqual(handle.get('hid'), 67712)

    def test_hids_to_handles_okay(self):
        self.start_test()
        handler = self.getImpl()

        hids = [68021, 68022]
        handles = handler.hids_to_handles(self.ctx, hids)[0]
        self.assertEqual(len(handles), 2)
        self.assertCountEqual(hids, [h.get('hid') for h in handles])
