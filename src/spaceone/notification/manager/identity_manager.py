import logging

from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core.manager import BaseManager
from spaceone.core.auth.jwt.jwt_util import JWTUtil

_LOGGER = logging.getLogger(__name__)

_GET_RESOURCE_METHODS = {
    "identity.Domain": {"dispatch_method": "Domain.get", "key": "domain_id"},
    "identity.Project": {"dispatch_method": "Project.get", "key": "project_id"},
    "identity.User": {"dispatch_method": "UserProfile.get", "key": "user_id"},
    "identity.ServiceAccount": {
        "dispatch_method": "ServiceAccount.get",
        "key": "service_account_id",
    },
}


class IdentityManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        token = self.transaction.get_meta("token")
        self.token_type = JWTUtil.get_value_from_token(token, "typ")
        self.identity_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="identity"
        )

    def get_resource(self, resource_id: str, resource_type: str, domain_id: str):
        get_method = _GET_RESOURCE_METHODS[resource_type]
        if self.token_type == "SYSTEM_TOKEN":
            return self.identity_connector.dispatch(
                get_method["dispatch_method"],
                {get_method["key"]: resource_id},
                x_domain_id=domain_id,
            )
        else:
            return self.identity_connector.dispatch(
                get_method["dispatch_method"], {get_method["key"]: resource_id}
            )

    def get_user_profile(self):
        return self.identity_connector.dispatch("UserProfile.get", {})

    def get_domain_info(self, domain_id: str) -> dict:
        if self.token_type == "SYSTEM_TOKEN":
            return self.identity_connector.dispatch(
                "Domain.get", {}, x_domain_id=domain_id
            )
        else:
            return self.identity_connector.dispatch("Domain.get", {})

    def get_all_users_in_domain(self, domain_id: str) -> list:
        query = {
            "state": "ENABLED",
        }

        if self.token_type == "SYSTEM_TOKEN":
            response = self.identity_connector.dispatch(
                "User.list", query, x_domain_id=domain_id
            )
        else:
            response = self.identity_connector.dispatch("User.list", query)
        return response.get("results", [])
