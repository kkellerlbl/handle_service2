
import logging
import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import subprocess
import traceback


class MongoUtil:

    def _start_service(self):
        logging.info('starting mongod service')

        logging.info('running sudo service mongodb start')
        pipe = subprocess.Popen("sudo service mongodb start", shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = pipe.communicate()
        logging.info(stdout)

        if stderr:
            raise ValueError('Cannot start mongodb')

        logging.info('running mongod --version')
        pipe = subprocess.Popen("mongod --version", shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = pipe.communicate()

        logging.info(stdout)

    def _insert_one(self, doc):
        """
        insert a doc into collection
        """

        try:
            self.handle_collection.insert_one(doc)
        except Exception as e:
            error_msg = 'Connot insert doc\n'
            error_msg += 'ERROR -- {}:\n{}'.format(
                            e,
                            ''.join(traceback.format_exception(None, e, e.__traceback__)))
            raise ValueError(error_msg)

    def _get_collection(self, mongo_host, mongo_port, mongo_database, mongo_collection):
        """
        connect Mongo server and return a collection
        """

        my_client = MongoClient(mongo_host, mongo_port)

        try:
            my_client.server_info()  # force a call to server
        except ServerSelectionTimeoutError as e:
            error_msg = 'Connot connect to Mongo server\n'
            error_msg += 'ERROR -- {}:\n{}'.format(
                            e,
                            ''.join(traceback.format_exception(None, e, e.__traceback__)))
            raise ValueError(error_msg)

        # TODO: check potential problems. MongoDB will create the collection if it does not exist.
        my_database = my_client[mongo_database]
        my_collection = my_database[mongo_collection]

        return my_collection

    def __init__(self, config):
        self.token = config['KB_AUTH_TOKEN']
        self.mongo_host = config['mongo-host']
        self.mongo_port = int(config['mongo-port'])
        self.mongo_database = config['mongo-database']
        self.mongo_collection = config['mongo-collection']

        self._start_service()
        self.handle_collection = self._get_collection(self.mongo_host, self.mongo_port,
                                                      self.mongo_database, self.mongo_collection)
