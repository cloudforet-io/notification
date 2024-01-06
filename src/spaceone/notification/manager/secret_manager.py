import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.notification.error import *

_LOGGER = logging.getLogger(__name__)


class SecretManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.secret_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="secret"
        )

    def create_secret(self, params):
        return self.secret_connector.dispatch("Secret.create", params)

    def update_secret(self, params):
        return self.secret_connector.dispatch("Secret.update", params)

    def update_secret_data(self, params):
        return self.secret_connector.dispatch("Secret.update_data", params)

    def delete_secret(self, secret_id: str):
        return self.secret_connector.dispatch("Secret.delete", {"secret_id": secret_id})

    def list_secrets(self, query, domain_id):
        return self.secret_connector.dispatch(
            "Secret.list", {"query": query, "domain_id": domain_id}
        )

    def get_secret_data(self, secret_id: str, domain_id: str):
        system_token = self.transaction.get_meta("token")
        response = self.secret_connector.dispatch(
            "Secret.get_data", {"secret_id": secret_id, "domain_id": domain_id}, token=system_token
        )
        return response["data"]

    def get_plugin_secret_data(self, secret_id, supported_schema, domain_id):
        secret_query = self._make_query(
            supported_schema=supported_schema, secret_id=secret_id
        )
        response = self.list_secrets(secret_query, domain_id)

        if response.get("total_count", 0) == 0:
            raise ERROR_NOT_FOUND(key="plugin_info.secret_id", value=secret_id)

        return self.get_secret_data(secret_id, domain_id)

    @staticmethod
    def _make_query(**secret_filter):
        supported_schema = secret_filter.get("supported_schema")
        secret_id = secret_filter.get("secret_id")
        service_account_id = secret_filter.get("service_account_id")
        project_id = secret_filter.get("project_id")
        provider = secret_filter.get("provider")
        secrets = secret_filter.get("secrets")

        query = {"filter": []}

        if supported_schema:
            query["filter"].append({"k": "schema", "v": supported_schema, "o": "in"})

        if secret_id:
            query["filter"].append({"k": "secret_id", "v": secret_id, "o": "eq"})

        if provider:
            query["filter"].append({"k": "provider", "v": provider, "o": "eq"})

        if service_account_id:
            query["filter"].append(
                {"k": "service_account_id", "v": service_account_id, "o": "eq"}
            )

        if project_id:
            query["filter"].append({"k": "project_id", "v": project_id, "o": "eq"})

        if secrets:
            query["filter"].append({"k": "secret_id", "v": secrets, "o": "in"})

        return query
