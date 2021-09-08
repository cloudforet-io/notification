import logging

from spaceone.core.manager import BaseManager
from spaceone.notification.error import *
from spaceone.notification.connector.repository_connector import RepositoryConnector

_LOGGER = logging.getLogger(__name__)


class RepositoryManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repo_connector: RepositoryConnector = self.locator.get_connector('RepositoryConnector')

    def get_plugin(self, plugin_id, domain_id):
        return self.repo_connector.get_plugin(plugin_id, domain_id)

    def get_schema(self, schema_name, domain_id):
        return self.repo_connector.get_schema(schema_name, domain_id)

    def get_plugin_versions(self, plugin_id, domain_id):
        return self.repo_connector.get_plugin_versions(plugin_id, domain_id)

    def check_plugin_version(self, plugin_id, version, domain_id):
        if version not in self.get_plugin_versions(plugin_id, domain_id):
            raise ERROR_INVALID_PLUGIN_VERSION(plugin_id=plugin_id, version=version)
