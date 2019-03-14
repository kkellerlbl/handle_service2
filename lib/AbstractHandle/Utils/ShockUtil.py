
import logging
import os
import traceback
import requests as _requests


class ShockUtil:

    def _get_hander(self):
        return {'Authorization': 'OAuth {}'.format(self.token)}

    def __init__(self, config):
        self.shock_url = config.get('shock-url')
        self.token = config.get('KB_AUTH_TOKEN')
        if not self.token:
            self.token = os.environ['KB_AUTH_TOKEN']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

    def get_owner(self, node_id):
        """
        parse owner.username information from shock acl of a node
        """

        headers = self._get_hander()

        end_point = os.path.join(self.shock_url, 'node', node_id, 'acl/?verbosity=full')

        resp = _requests.get(end_point, headers=headers)

        if resp.status_code != 200:
            raise ValueError('Request owner failed.\nError Code: {}\n{}\n'
                             .format(resp.status_code, resp.text))
        else:
            data = resp.json()
            try:
                owner = data.get('data').get('owner').get('username')
            except AttributeError as e:
                error_msg = 'Connot parse owner information from reponse\n'
                error_msg += 'ERROR -- {}:\n{}'.format(
                            e,
                            ''.join(traceback.format_exception(None, e, e.__traceback__)))
                raise ValueError(error_msg)
            else:
                return owner

    def is_readable(self, node_id):
        """
        check if a node is reachable/readable
        """

        headers = self._get_hander()

        end_point = os.path.join(self.shock_url, 'node', node_id)

        resp = _requests.get(end_point, headers=headers)

        if resp.ok:
            return True
        else:
            return False
