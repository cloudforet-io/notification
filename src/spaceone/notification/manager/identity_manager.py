import logging

from spaceone.core import config
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core.manager import BaseManager

_LOGGER = logging.getLogger(__name__)

_GET_RESOURCE_METHODS = {
    "identity.Domain": {"dispatch_method": "Domain.get", "key": "domain_id"},
    "identity.Project": {"dispatch_method": "Project.get", "key": "project_id"},
    "identity.User": {"dispatch_method": "User.get", "key": "user_id"},
    "identity.ServiceAccount": {
        "dispatch_method": "ServiceAccount.get",
        "key": "service_account_id",
    },
}


class IdentityManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="identity"
        )

    def get_resource(self, resource_id: str, resource_type: str):
        get_method = _GET_RESOURCE_METHODS[resource_type]
        return self.identity_connector.dispatch(
            get_method["dispatch_method"],
            {get_method["key"]: resource_id},
        )

    def get_domain_info(self, domain_id):
        token = config.get_global("TOKEN")
        return self.identity_connector.dispatch(
            "Domain.get", {"domain_id": domain_id}, token=token
        )

    def get_all_users_in_domain(self):
        query = {
            "state": "ENABLED",
        }

        response = self.identity_connector.dispatch("User.list", query)
        return response.get("results", [])
