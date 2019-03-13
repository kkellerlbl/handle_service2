
import logging
import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import subprocess
import traceback

from AbstractHandle.Utils.MongoUtil import MongoUtil


class Handler:

    @staticmethod
    def validate_params(params, expected, opt_param=set()):
        """Validates that required parameters are present. Warns if unexpected parameters appear"""
        expected = set(expected)
        opt_param = set(opt_param)
        pkeys = set(params)
        if expected - pkeys:
            raise ValueError("Required keys {} not in supplied parameters"
                             .format(", ".join(expected - pkeys)))
        defined_param = expected | opt_param
        for param in params:
            if param not in defined_param:
                logging.warning("Unexpected parameter {} supplied".format(param))

    def __init__(self, config):
        self.token = config['KB_AUTH_TOKEN']
        self.mongo_util = MongoUtil(config)

    def fetch_handles_by(self, params):

        self.validate_params(params, ['elements', 'field_name'])

        elements = params.get('elements')
        field_name = params.get('field_name')

        docs = self.mongo_util.find_in(elements, field_name)

        handles = list()
        for doc in docs:
            handles.append(doc)

        return handles
