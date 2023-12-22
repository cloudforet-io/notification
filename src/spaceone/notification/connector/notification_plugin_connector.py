import logging

from google.protobuf.json_format import MessageToDict

from spaceone.core.connector import BaseConnector
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core import pygrpc
from spaceone.core.utils import parse_endpoint

__all__ = ["NotificationPluginConnector"]
_LOGGER = logging.getLogger(__name__)


class NotificationPluginConnector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.noti_plugin_connector = None

    def initialize(self, endpoint):
        static_endpoint = self.config.get("endpoint")

        if static_endpoint:
            endpoint = static_endpoint

        self.noti_plugin_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint
        )

    def init(self, options):
        response = self.noti_plugin_connector.dispatch(
            "Protocol.init", {"options": options}
        )
        return self._change_message(response)

    def verify(self, options, secret_data):
        params = {"options": options, "secret_data": secret_data}

        self.noti_plugin_connector.dispatch("Protocol.verify", params)

    def dispatch_notification(
        self, secret_data: dict, channel_data, notification_type, message, options={}
    ):
        params = {
            "secret_data": secret_data,
            "channel_data": channel_data,
            "notification_type": notification_type,
            "message": message,
            "options": options,
        }

        response = self.noti_plugin_connector.dispatch("Notification.dispatch", params)
        return self._change_message(response)

    @staticmethod
    def _change_message(message):
        return MessageToDict(message, preserving_proto_field_name=True)
