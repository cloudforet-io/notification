import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.notification.error import *

_LOGGER = logging.getLogger(__name__)


class RepositoryManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repo_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="repository"
        )

    def get_plugin(self, plugin_id: str):
        return self.repo_connector.dispatch("Plugin.get", {"plugin_id": plugin_id})

    def get_plugin_versions(self, plugin_id):
        return self.repo_connector.dispatch(
            "Plugin.get_versions", {"plugin_id": plugin_id}
        )

    def check_plugin_version(self, plugin_id: str, version: str) -> None:
        if version not in self.get_plugin_versions(plugin_id):
            raise ERROR_INVALID_PLUGIN_VERSION(plugin_id=plugin_id, version=version)
