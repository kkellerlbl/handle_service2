# -*- coding: utf-8 -*-
import os
import unittest
from configparser import ConfigParser
import inspect

from AbstractHandle.authclient import KBaseAuth as _KBaseAuth

from AbstractHandle.Utils.ShockUtil import ShockUtil


class HandlerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {'KB_AUTH_TOKEN': cls.token}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('AbstractHandle'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        cls.user_id = auth_client.get_user(cls.token)

        cls.shock_util = ShockUtil(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        print('Finished testing ShockUtil')

    def getShockUtil(self):
        return self.__class__.shock_util

    def getNodeID(self):
        node_id = 'a31db49f-447c-4fff-96d5-2981166c0b9b'  # for the simplicity using one of `tgu2` node

        return node_id

    def start_test(self):
        testname = inspect.stack()[1][3]
        print('\n*** starting test: ' + testname + ' **')

    def test_init_ok(self):
        self.start_test()
        class_attri = ['token', 'shock_url']
        shock_util = self.getShockUtil()
        self.assertTrue(set(class_attri) <= set(shock_util.__dict__.keys()))

    def test_get_owner_fail(self):
        self.start_test()
        shock_util = self.getShockUtil()

        node_id = 'fake_node_id'
        with self.assertRaises(ValueError) as context:
            shock_util.get_owner(node_id)

        self.assertIn('Request owner failed', str(context.exception.args))

    def test_get_owner_ok(self):
        self.start_test()
        shock_util = self.getShockUtil()
        node_id = self.getNodeID()

        owner = shock_util.get_owner(node_id)

        self.assertEqual(owner, 'tgu2')

    def test_is_readable_ok(self):
        self.start_test()
        shock_util = self.getShockUtil()
        node_id = self.getNodeID()

        is_readable = shock_util.is_readable(node_id)
        self.assertTrue(is_readable)

        node_id = 'fake_node_id'
        is_readable = shock_util.is_readable(node_id)
        self.assertFalse(is_readable)
