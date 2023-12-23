import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.notification.error import *

_LOGGER = logging.getLogger(__name__)


class UserSecretManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.secret_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="secret"
        )

    def create_user_secret(self, params):
        return self.secret_connector.dispatch("UserSecret.create", params)

    def update_secret(self, params):
        return self.secret_connector.dispatch("UserSecret.update", params)

    def update_user_secret_data(self, params):
        return self.secret_connector.dispatch("UserSecret.update_data", params)

    def delete_user_secret(self, secret_id: str):
        return self.secret_connector.dispatch(
            "UserSecret.delete", {"secret_id": secret_id}
        )

    def list_secrets(self, query, domain_id):
        return self.secret_connector.dispatch(
            "UserSecret.list", {"query": query, "domain_id": domain_id}
        )

    def get_secret_data(self, secret_id, domain_id):
        response = self.secret_connector.dispatch(
            "UserSecret.get_data", {"secret_id": secret_id, "domain_id": domain_id}
        )
        return response["data"]
