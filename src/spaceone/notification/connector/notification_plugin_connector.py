import logging

from spaceone.core.connector import BaseConnector
from spaceone.core.connector.space_connector import SpaceConnector

__all__ = ["NotificationPluginConnector"]
_LOGGER = logging.getLogger(__name__)


class NotificationPluginConnector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.noti_plugin_connector = None

    def initialize(self, endpoint: str):
        static_endpoint = self.config.get("endpoint")

        if static_endpoint:
            endpoint = static_endpoint

        self.noti_plugin_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint, token="NO_TOKEN"
        )

    def init(self, options, domain_id=None):
        return self.noti_plugin_connector.dispatch(
            "Protocol.init", {"options": options}
        )

    def verify(self, options, secret_data):
        params = {"options": options, "secret_data": secret_data}

        self.noti_plugin_connector.dispatch("Protocol.verify", params)

    def dispatch_notification(
            self, secret_data: dict, channel_data, notification_type, message, options={}, domain_id=None
    ):
        params = {
            "secret_data": secret_data,
            "channel_data": channel_data,
            "notification_type": notification_type,
            "message": message,
            "options": options,
        }

        return self.noti_plugin_connector.dispatch("Notification.dispatch", params)
