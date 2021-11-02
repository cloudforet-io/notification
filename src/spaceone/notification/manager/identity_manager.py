import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

_LOGGER = logging.getLogger(__name__)

_GET_RESOURCE_METHODS = {
    'identity.Project': {
        'dispatch_method': 'Project.get',
        'key': 'project_id'
    },
    'identity.User': {
        'dispatch_method': 'User.get',
        'key': 'user_id'
    },
    'identity.ServiceAccount': {
        'dispatch_method': 'ServiceAccount.get',
        'key': 'service_account_id'
    },
}

class IdentityManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='identity')

    def get_resource(self, resource_id, resource_type, domain_id):
        get_method = _GET_RESOURCE_METHODS[resource_type]
        return self.identity_connector.dispatch(get_method['dispatch_method'], {get_method['key']: resource_id, 'domain_id': domain_id})
