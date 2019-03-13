
import logging
from time import gmtime, strftime
import uuid

from AbstractHandle.authclient import KBaseAuth as _KBaseAuth
from AbstractHandle.Utils.MongoUtil import MongoUtil
import copy


class Handler:

    FIELD_NAMES = ['hid', 'id', 'file_name', 'type', 'url', 'remote_md5', 'remote_sha1',
                   'created_by', 'creation_date']

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

    def _process_handle(self, handle, user_id):
        """
        pre-process handle: check/remove/add fields
        """
        logging.info('start processing handle')

        handle = {k: v for k, v in handle.items() if k in self.FIELD_NAMES}  # remove unnecessary fields
        if not handle.get('hid'):
            handle['hid'] = str(uuid.uuid4())

        handle['_id'] = handle.get('hid')  # assign _id to hid

        required_fields = ['id', 'file_name', 'type', 'url']
        fields_values = [v for k, v in handle.items() if k in required_fields]
        if (len(fields_values) != len(required_fields)) or (not all(fields_values)):
            error_msg = 'Missing one or more required positional field\n'
            error_msg += 'Requried fields: {}'.format(required_fields)
            raise ValueError(error_msg)

        if not handle.get('remote_md5'):  # assign None to remote_md5/remote_sha1 if missing/empty
            handle['remote_md5'] = None

        if not handle.get('remote_sha1'):
            handle['remote_sha1'] = None

        if not handle.get('created_by'):  # assign created_by to current token user if missing
            handle['created_by'] = user_id

        if not handle.get('creation_date'):  # assign creation_date if missing
            handle['creation_date'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        return handle

    def __init__(self, config):
        self.token = config['KB_AUTH_TOKEN']
        authServiceUrl = config['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        self.user_id = auth_client.get_user(self.token)
        self.mongo_util = MongoUtil(config)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

    def fetch_handles_by(self, params):
        logging.info('start fetching handles')

        self.validate_params(params, ['elements', 'field_name'])

        elements = params.get('elements')
        field_name = params.get('field_name')

        docs = self.mongo_util.find_in(elements, field_name)

        handles = list()
        for doc in docs:
            handles.append(doc)

        return handles

    def persist_handle(self, handle, user_id):
        logging.info('start persisting handle')

        handle = self._process_handle(handle, user_id)
        hid = handle.get('hid')

        try:
            hid = int(hid)
        except Exception:
            pass

        docs = self.mongo_util.find_in([hid], 'hid')

        if docs.count():
            # handle exists, update handle
            if handle.get('created_by') != user_id:
                raise ValueError('Cannot update handle not created by owner')

            self.mongo_util.update_one(handle)
        else:
            # handle doesn't exist, insert handle
            self.mongo_util.insert_one(handle)

        return str(hid)
