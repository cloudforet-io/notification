from spaceone.core import utils
from spaceone.core.service import *
from spaceone.notification.error import *
from spaceone.notification.manager import IdentityManager
from spaceone.notification.manager import ProtocolManager
from spaceone.notification.manager import ProjectChannelManager
from spaceone.notification.manager import SecretManager
from spaceone.notification.model import ProjectChannel


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProjectChannelService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.project_channel_mgr: ProjectChannelManager = self.locator.get_manager('ProjectChannelManager')
        self.identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
        self.protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')
        self.secret_mgr: SecretManager = self.locator.get_manager('SecretManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['protocol_id', 'name', 'schema', 'data', 'project_id', 'domain_id'])
    def create(self, params):

        """ Create Project Channel

        Args:
            params (dict): {
                'protocol_id': 'str',
                'name': 'str',
                'schema': 'str',
                'data': 'dict',
                'subscriptions': 'list',
                'notification_level': 'str',
                'schedule': 'dict',
                'project_id': 'str',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            project_channel_vo (object)

        """
        protocol_id = params['protocol_id']
        domain_id = params['domain_id']
        data = params['data']
        schema = params['schema']
        project_id = params['project_id']
        is_subscribe = params.get('is_subscribe')

        if is_subscribe:
            new_subscriptions = params.get('subscriptions', [])
            params['subscriptions'] = new_subscriptions
        else:
            if 'is_subscribe' in params:
                del params['is_subscribe']
            if 'subscriptions' in params:
                del params['subscriptions']

        # Check project_id exists
        self.identity_mgr.get_resource(project_id, 'identity.Project', domain_id)
        protocol_vo = self.protocol_mgr.get_protocol(protocol_id, domain_id)
        capability = protocol_vo.capability

        if capability.get('data_type') == 'SECRET':
            secret_name = utils.generate_id('project-channel', 4)
            new_secret_parameters = {
                "name": f'{secret_name}',
                "secret_type": "CREDENTIALS",
                "data": data,
                "schema": schema,
                "domain_id": domain_id
            }

            project_channel_secret = self.secret_mgr.create_secret(new_secret_parameters)
            params['secret_id'] = project_channel_secret.get('secret_id')

        # Create Protocol
        project_channel_vo: ProjectChannel = self.project_channel_mgr.create_project_channel(params)

        return project_channel_vo

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['project_channel_id', 'domain_id'])
    def update(self, params):

        """ Update project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'name': 'str',
                'data': 'dict',
                'notification_level': 'str',
                'schedule': 'dict',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            project_channel_vo (object)
        """

        return self.project_channel_mgr.update_project_channel(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['project_channel_id', 'domain_id'])
    def set_subscription(self, params):
        """ Update project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'is_subscribe': bool,
                'is_subscribe': list,
                'domain_id': 'str'
            }

        Returns:
            project_channel_vo (object)
        """
        if params.get('is_subscribe') == False or 'is_subscribe' not in params:
            params['is_subscribe'] = False
            params['subscriptions'] = []
        else:
            params['subscriptions'] = params.get('subscriptions')

        return self.project_channel_mgr.update_project_channel(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['project_channel_id', 'domain_id'])
    def delete(self, params):
        """ Delete project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.project_channel_mgr.delete_project_channel(params['project_channel_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['project_channel_id', 'domain_id'])
    def enable(self, params):
        """ Enable project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            project_channel_vo (object)
        """

        return self.project_channel_mgr.enable_project_channel(params['project_channel_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['project_channel_id', 'domain_id'])
    def disable(self, params):
        """ Disable project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            project_channel_vo (object)
        """

        return self.project_channel_mgr.disable_project_channel(params['project_channel_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['project_channel_id', 'domain_id'])
    def get(self, params):
        """ Get Project Channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'only': 'list'
            }

        Returns:
            project_channel_vo (object)
        """

        return self.project_channel_mgr.get_project_channel(params['project_channel_id'], params['domain_id'],
                                                            params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['project_channel_id', 'name', 'state', 'schema', 'secret_id', 'notification_level', 'protocol_id', 'project_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['project_channel_id'])
    def list(self, params):
        """ List Project Channels

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'name': 'str',
                'state': 'str',
                'schema': 'str',
                'secret_id': 'str',
                'notification_level': 'str',
                'protocol_id': 'str',
                'project_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)',
                'domain_id': 'str'
            }

        Returns:
            results (list): 'list of project_channel_vo'
            total_count (int)
        """

        query = params.get('query', {})
        return self.project_channel_mgr.list_project_channels(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['project_channel_id', 'name'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """
        query = params.get('query', {})
        return self.project_channel_mgr.stat_project_channels(query)

