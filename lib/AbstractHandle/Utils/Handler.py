
import logging
from time import gmtime, strftime
import uuid

from AbstractHandle.Utils.MongoUtil import MongoUtil
from AbstractHandle.Utils.ShockUtil import ShockUtil


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

    def _get_admin_users(self, config):
        """
        fetch admin users for handle service who can grant shock acl
        """
        admin_users = list()
        allowed_users = config.get('allowed-users')

        if isinstance(allowed_users, list):
            admin_users.extend(allowed_users)
        else:
            admin_users.extend(allowed_users.split(','))

        return list(set(admin_users))

    def __init__(self, config):
        self.mongo_util = MongoUtil(config)
        self.shock_util = ShockUtil(config)

        self.admin_users = self._get_admin_users(config)

        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

    def fetch_handles_by(self, params):
        """
        query DB and return if element match one of entry in field column
        """
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
        """
        writes the handle to a persistent store

        insert handle if handle does not exist
        otherwise update handle if it's created by token user
        """
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

    def delete_handles(self, handles, user_id):
        """
        delete handles

        raise error if any of handles are not created by token user
        """

        handle_user = set([h.get('created_by') for h in handles])

        if not (handle_user == set([user_id])):
            raise ValueError('Cannot delete handles not created by owner')

        deleted_count = self.mongo_util.delete_many(handles)

        return deleted_count

    def is_owner(self, hids, user_id):
        """
        check and see if token user is owner.username from shock node
        """

        handles = self.fetch_handles_by({'elements': hids, 'field_name': 'hid'})

        for handle in handles:
            node_type = handle.get('type')
            if node_type != 'shock':
                raise ValueError('Do not support node type other than Shock')

            node_id = handle.get('id')
            owner = self.shock_util.get_owner(node_id)

            if owner != user_id:
                return False

        return True

    def are_readable(self, hids):
        """
        check if nodes associated with handles is reachable/readable
        """

        handles = self.fetch_handles_by({'elements': hids, 'field_name': 'hid'})

        for handle in handles:
            node_type = handle.get('type')
            if node_type != 'shock':
                raise ValueError('Do not support node type other than Shock')

            node_id = handle.get('id')

            is_readable = self.shock_util.is_readable(node_id)

            if not is_readable:
                return False

        return True

    def add_read_acl(self, hids, user_id, username=None):
        """
        grand readable acl for username or global if username is empty
        """

        if user_id not in self.admin_users:
            raise ValueError('User {} may not run add_read_acl/set_public_read method'.format(user_id))

        handles = self.fetch_handles_by({'elements': hids, 'field_name': 'hid'})

        for handle in handles:
            node_type = handle.get('type')
            if node_type != 'shock':
                raise ValueError('Do not support node type other than Shock')

            node_id = handle.get('id')
            self.shock_util.add_read_acl(node_id, username=username)

        return True
