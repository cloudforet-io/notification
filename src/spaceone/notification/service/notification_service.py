from spaceone.core import utils
from spaceone.core.service import *
from spaceone.notification.manager import IdentityManager
from spaceone.notification.manager import NotificationManager
from spaceone.notification.manager import ProtocolManager
from spaceone.notification.manager import SecretManager
from spaceone.notification.model import Notification

@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class NotificationService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.notification_mgr: NotificationManager = self.locator.get_manager('NotificationManager')
        self.identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
        self.protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')
        self.secret_mgr: SecretManager = self.locator.get_manager('SecretManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['resource_type', 'resource_id', 'topic', 'message', 'domain_id'])
    def create(self, params):
        """ Create Notification

        Args:
            params (dict): {
                'resource_type': 'str' -> identity.Project | identity.User,
                'resource_id': 'str',
                'topic': 'str',
                'message': 'dict',
                'notification_type': 'str' -> INFO | ERROR | SUCCESS | WARNING,
                'notification_level': 'str' -> ALL(default) | LV1 | LV2 | LV3 | LV4 | LV5,
                'domain_id': 'str'
            }

        Returns:
            notification_vo (object)
        """
        domain_id = params['domain_id']
        resource_type = params['resource_type']
        resource_id = params['resource_id']

        # Check project_id or user_id exists
        self.identity_mgr.get_resource(resource_id, resource_type, domain_id)
        # identity.Project | identity.User
        handling_resource_key = 'project_id' if resource_type == 'identity.Project' else 'user_id'
        params.update({handling_resource_key: resource_id})

        # TODO:: If parsed message has parents_notification_id, then filter it and add parents_code
        notification_vo: Notification = self.notification_mgr.create_notification(params)

        return notification_vo

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['notification_id', 'domain_id'])
    def delete(self, params):
        """ Delete notification

        Args:
            params (dict): {
                'user_channel_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.notification_mgr.delete_notification(params['notification_id'],
                                                  params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['notification_id', 'domain_id'])
    def get(self, params):

        """ Get Notification

        Args:
            params (dict): {
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            notification_vo (object)
        """

        return self.notification_mgr.get_notification(params['notification_id'],
                                                      params['domain_id'],
                                                      params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['notification_id', 'topic', 'notificaion_type', 'notificaion_level', 'parent_notificaion_id', 'project_id', 'user_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['user_channel_id'])
    def list(self, params):
        """ List User Channels

        Args:
            params (dict): {
                'user_channel_id': 'str',
                'name': 'str',
                'state': 'str',
                'schema': 'str',
                'secret_id': 'str',
                'protocol_id': 'str',
                'user_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)',
                'domain_id': 'str'
            }

        Returns:
            results (list): 'list of user_channel_vo'
            total_count (int)
        """

        query = params.get('query', {})
        return self.notification_mgr.list_notifications(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['notification_id', 'topic'])
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
        return self.notification_mgr.stat_notifications(query)
