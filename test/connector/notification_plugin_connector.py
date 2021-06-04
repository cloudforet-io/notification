import logging

from google.protobuf.json_format import MessageToDict

from spaceone.core.connector import BaseConnector
from spaceone.core import pygrpc
from spaceone.core.utils import parse_endpoint
from pprint import pprint
from spaceone.core.error import *

__all__ = ['NotificationPluginConnector']

_LOGGER = logging.getLogger(__name__)


class NotificationPluginConnector(BaseConnector):

    def __init__(self, transaction, config):
        super().__init__(transaction, config)
        self.client = None

    def initialize(self, endpoint):
        static_endpoint = self.config.get('endpoint')

        if static_endpoint:
            endpoint = static_endpoint

        e = parse_endpoint(endpoint)
        self.client = pygrpc.client(endpoint=f'{e.get("hostname")}:{e.get("port")}', version='plugin')

    def init(self, options):
        response = self.client.Webhook.init({
            'options': options,
        }, metadata=self.transaction.get_connection_meta())

        return self._change_message(response)

    def verify(self, options, secret_data, schema=None):
        params = {
            'options': options,
            'secret_data': secret_data
        }

        if schema:
            params.update({
                'schema': schema
            })

        self.client.Webhook.verify(params, metadata=self.transaction.get_connection_meta())

    def dispatch(self, options, message, notification_type):
        params = {
            'options': options,
            'message': message,
            'notification_type': notification_type
        }

        response = self.client.Notification.dispatch(params, metadata=self.transaction.get_connection_meta())
        return self._change_message(response)

    @staticmethod
    def _change_message(message):
        return MessageToDict(message, preserving_proto_field_name=True)