# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
import inspect
import copy

from AbstractHandle.AbstractHandleImpl import AbstractHandle
from AbstractHandle.AbstractHandleServer import MethodContext
from AbstractHandle.authclient import KBaseAuth as _KBaseAuth
from AbstractHandle.Utils.MongoUtil import MongoUtil

from installed_clients.WorkspaceClient import Workspace

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
        cls.user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': cls.user_id,
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
        cls.mongo_helper = MongoHelper()
        cls.my_client = cls.mongo_helper.create_test_db(db=cls.cfg['mongo-database'],
                                                        col=cls.cfg['mongo-collection'])
        cls.mongo_util = MongoUtil(cls.cfg)

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

    def start_test(self):
        testname = inspect.stack()[1][3]
        print('\n*** starting test: ' + testname + ' **')

    def test_fetch_handles_by_ok(self):
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

    def test_ids_to_handles_ok(self):
        self.start_test()
        handler = self.getImpl()

        ids = ['b753774f-0bbd-4b96-9202-89b0c70bf31c']
        handles = handler.ids_to_handles(self.ctx, ids)[0]
        self.assertEqual(len(handles), 1)
        handle = handles[0]
        self.assertFalse('_id' in handle)
        self.assertEqual(handle.get('hid'), 67712)

    def test_hids_to_handles_ok(self):
        self.start_test()
        handler = self.getImpl()

        hids = [68021, 68022]
        handles = handler.hids_to_handles(self.ctx, hids)[0]
        self.assertEqual(len(handles), 2)
        self.assertCountEqual(hids, [h.get('hid') for h in handles])

    def test_persist_handle_ok(self):
        self.start_test()
        handler = self.getImpl()

        handle = {'id': 'id',
                  'file_name': 'file_name',
                  'type': 'shock',
                  'url': 'http://ci.kbase.us:7044/'}
        # testing persist_handle with non-existing handle (inserting a handle)
        hid = handler.persist_handle(self.ctx, handle)[0]
        handles = handler.fetch_handles_by(self.ctx, {'elements': [hid], 'field_name': 'hid'})[0]
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
        new_hid = handler.persist_handle(self.ctx, new_handle)[0]
        handles = handler.fetch_handles_by(self.ctx, {'elements': [new_hid], 'field_name': 'hid'})[0]
        self.assertEqual(len(handles), 1)
        handle = handles[0]
        self.assertEqual(handle.get('hid'), new_hid)
        self.assertEqual(handle.get('id'), new_id)
        self.assertEqual(handle.get('file_name'), new_file_name)
        self.assertEqual(handle.get('created_by'), self.user_id)

        self.assertEqual(new_hid, hid)

        self.mongo_util.delete_one(handle)

    def test_delete_handles_ok(self):
        self.start_test()
        handler = self.getImpl()

        handles = [{'id': 'id',
                    'file_name': 'file_name',
                    'type': 'shock',
                    'url': 'http://ci.kbase.us:7044/'}] * 2
        hids_to_delete = list()
        for handle in handles:
            hid = handler.persist_handle(self.ctx, handle)[0]
            hids_to_delete.append(hid)

        handles_to_delete = handler.fetch_handles_by(self.ctx, {'elements': hids_to_delete, 'field_name': 'hid'})[0]

        delete_count = handler.delete_handles(self.ctx, handles_to_delete)[0]

        self.assertEqual(delete_count, len(hids_to_delete))

    def test_is_owner_ok(self):
        self.start_test()
        handler = self.getImpl()

        handles = [{'id': 'id',
                    'file_name': 'file_name',
                    'type': 'shock',
                    'url': 'http://ci.kbase.us:7044/'}] * 2
        hids = list()
        for handle in handles:
            # create handles created by current token user
            hid = handler.persist_handle(self.ctx, handle)[0]
            hids.append(hid)

        is_owner = handler.is_owner(self.ctx, hids)[0]
        self.assertTrue(is_owner)

        new_handle = {'id': 'id',
                      'file_name': 'file_name',
                      'type': 'shock',
                      'url': 'http://ci.kbase.us:7044/',
                      'created_by': 'fake_user'}
        # create a handle created by current token user
        new_hid = handler.persist_handle(self.ctx, new_handle)[0]
        hids.append(new_hid)

        is_owner = handler.is_owner(self.ctx, hids)[0]
        self.assertFalse(is_owner)

        new_handles = handler.fetch_handles_by(self.ctx, {'elements': hids, 'field_name': 'hid'})[0]

        for handle in new_handles:
            self.mongo_util.delete_one(handle)
