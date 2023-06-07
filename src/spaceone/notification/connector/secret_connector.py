"""
Deprecated:
  Not used. Integrated with SpaceConnector.
"""

import logging

from google.protobuf.json_format import MessageToDict

from spaceone.core.connector import BaseConnector
from spaceone.core import pygrpc
from spaceone.core.utils import parse_endpoint
from spaceone.core.error import *

__all__ = ['SecretConnector']

_LOGGER = logging.getLogger(__name__)


class SecretConnector(BaseConnector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._check_config()
        self._init_client()

    def _init_client(self):
        for version, uri in self.config['endpoint'].items():
            e = parse_endpoint(uri)
            self.client = pygrpc.client(endpoint=f'{e.get("hostname")}:{e.get("port")}', version=version)

    def _check_config(self):
        if 'endpoint' not in self.config:
            raise ERROR_CONNECTOR_CONFIGURATION(connector=self.__class__.__name__)

        if len(self.config['endpoint']) > 1:
            raise ERROR_CONNECTOR_CONFIGURATION(connector=self.__class__.__name__)

    def create_secret(self, params):
        response = self.client.Secret.create(params, metadata=self.transaction.get_connection_meta())
        return self._change_message(response)

    def update_secret(self, params):
        response = self.client.Secret.update(params, metadata=self.transaction.get_connection_meta())
        return self._change_message(response)

    def update_secret_data(self, params):
        response = self.client.Secret.update_data(params, metadata=self.transaction.get_connection_meta())
        return self._change_message(response)

    def delete_secret(self, params):
        self.client.Secret.delete(params, metadata=self.transaction.get_connection_meta())

    def list_secrets(self, query, domain_id):
        response = self.client.Secret.list({
            'query': query,
            'domain_id': domain_id
        }, metadata=self.transaction.get_connection_meta())

        return self._change_message(response)

    def get_secret_data(self, secret_id, domain_id):
        response = self.client.Secret.get_data({
            'secret_id': secret_id,
            'domain_id': domain_id
        }, metadata=self.transaction.get_connection_meta())

        return self._change_message(response)

    @staticmethod
    def _change_message(message):
        return MessageToDict(message, preserving_proto_field_name=True)
