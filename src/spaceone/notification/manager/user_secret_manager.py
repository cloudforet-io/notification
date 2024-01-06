import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

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

    def delete_user_secret(self, user_secret_id: str):
        return self.secret_connector.dispatch(
            "UserSecret.delete", {"user_secret_id": user_secret_id}
        )

    def list_user_secrets(self, query, domain_id):
        return self.secret_connector.dispatch(
            "UserSecret.list", {"query": query, "domain_id": domain_id}
        )

    def get_user_secret_data(self, user_secret_id: str, domain_id: str) -> dict:
        system_token = self.transaction.get_meta("token")
        response = self.secret_connector.dispatch(
            "UserSecret.get_data",
            {"user_secret_id": user_secret_id, "domain_id": domain_id},
            token=system_token
        )
        return response["data"]
