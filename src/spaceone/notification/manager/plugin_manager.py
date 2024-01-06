import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

from spaceone.notification.connector.notification_plugin_connector import (
    NotificationPluginConnector,
)

_LOGGER = logging.getLogger(__name__)


class PluginManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="plugin"
        )
        self.noti_plugin_connector: NotificationPluginConnector = (
            self.locator.get_connector(NotificationPluginConnector)
        )

    def initialize(self, plugin_info: dict, domain_id: str) -> dict:
        _LOGGER.debug(f"[initialize] plugin_info: {plugin_info}")

        plugin_id = plugin_info["plugin_id"]
        upgrade_mode = plugin_info.get("upgrade_mode", "AUTO")

        if upgrade_mode == "AUTO":
            params = {
                "plugin_id": plugin_id,
                "domain_id": domain_id,
                "upgrade_mode": "AUTO"
            }
        else:
            params = {
                "plugin_id": plugin_id,
                "domain_id": domain_id,
                "version": plugin_info.get("version"),
            }

        system_token = self.transaction.get_meta("token")
        endpoint_response = self.plugin_connector.dispatch(
            "Plugin.get_plugin_endpoint",
            params,
            token=system_token,
        )

        endpoint = endpoint_response["endpoint"]
        _LOGGER.debug(f"[init_plugin] endpoint: {endpoint}")
        self.noti_plugin_connector.initialize(endpoint)

        return endpoint_response

    def init_plugin(self, options: dict, domain_id: str = None) -> dict:
        plugin_info = self.noti_plugin_connector.init(options, domain_id)

        _LOGGER.debug(f"[plugin_info] {plugin_info}")
        return plugin_info.get("metadata", {})

    def verify_plugin(self, options, secret_data):
        self.noti_plugin_connector.verify(options, secret_data)

    def dispatch_notification(
            self, secret_data, channel_data, notification_type, message, options, domain_id
    ):
        return self.noti_plugin_connector.dispatch_notification(
            secret_data, channel_data, notification_type, message, options, domain_id
        )
