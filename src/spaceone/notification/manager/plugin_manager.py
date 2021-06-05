import logging

from spaceone.core.manager import BaseManager
from spaceone.notification.error import *
from spaceone.notification.connector.plugin_connector import PluginConnector
from spaceone.notification.connector.notification_plugin_connector import NotificationPluginConnector

_LOGGER = logging.getLogger(__name__)


class PluginManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_connector: PluginConnector = self.locator.get_connector('PluginConnector')
        self.noti_plugin_connector: NotificationPluginConnector = self.locator.get_connector(
            'NotificationPluginConnector')

    def initialize(self, plugin_id, version, domain_id):
        endpoint = self.plugin_connector.get_plugin_endpoint(plugin_id, version, domain_id)
        _LOGGER.debug(f'[init_plugin] endpoint: {endpoint}')
        self.noti_plugin_connector.initialize(endpoint)

    def init_plugin(self, options):
        plugin_info = self.noti_plugin_connector.init(options)

        _LOGGER.debug(f'[plugin_info] {plugin_info}')
        return plugin_info.get('metadata', {})

    def verify_plugin(self, options, secret_data):
        self.noti_plugin_connector.verify(options, secret_data)

    def dispatch_notification(self, secret_data, notification_type, message, options):
        return self.noti_plugin_connector.dispatch_notification(secret_data, notification_type, message, options)
