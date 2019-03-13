# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
import inspect

from AbstractHandle.authclient import KBaseAuth as _KBaseAuth

from mongo_util import MongoHelper
from AbstractHandle.Utils.MongoUtil import MongoUtil


class MongoUtilTest(unittest.TestCase):

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
        cls.mongo_util = MongoUtil(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getMongoUtil(self):
        return self.__class__.mongo_util

    def start_test(self):
        testname = inspect.stack()[1][3]
        print('\n*** starting test: ' + testname + ' **')

    def test_get_collection(self):
        self.start_test()
        mongo_util = self.getMongoUtil()
        with self.assertRaises(ValueError) as context:
            mongo_util._get_collection('fake_mongo_host', 1234, 'mongo_database', 'mongo_collection')

        self.assertIn('Connot connect to Mongo server', str(context.exception.args))

    def test_init_ok(self):
        self.start_test()
        class_attri = ['token', 'mongo_host', 'mongo_port', 'mongo_database', 'mongo_collection']
        mongo_util = self.getMongoUtil()
        self.assertTrue(set(class_attri) <= set(mongo_util.__dict__.keys()))

        handle_collection = mongo_util.handle_collection
        self.assertEqual(handle_collection.name, 'handle')
        self.assertEqual(handle_collection.count_documents({}), 10)

    def test_find_in_ok(self):
        self.start_test()

        mongo_util = self.getMongoUtil()

        # test query 'hid' field
        elements = [68021, 68022]
        docs = mongo_util.find_in(elements, 'hid')
        self.assertEqual(docs.count(), 2)

        # test query 'hid' field with empty data
        elements = [0]
        docs = mongo_util.find_in(elements, 'hid')
        self.assertEqual(docs.count(), 0)

        # test query 'id' field
        elements = ['b753774f-0bbd-4b96-9202-89b0c70bf31c']
        docs = mongo_util.find_in(elements, 'id')
        self.assertEqual(docs.count(), 1)
        doc = docs.next()
        self.assertFalse('_id' in doc.keys())
        self.assertEqual(doc.get('hid'), 67712)

        # test null projection
        elements = ['b753774f-0bbd-4b96-9202-89b0c70bf31c']
        docs = mongo_util.find_in(elements, 'id', projection=None)
        self.assertEqual(docs.count(), 1)
        doc = docs.next()
        self.assertEqual(doc.get('_id'), 67712)
        self.assertEqual(doc.get('hid'), 67712)
