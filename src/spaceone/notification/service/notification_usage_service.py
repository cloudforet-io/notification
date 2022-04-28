import logging
from spaceone.core.service import *
from spaceone.notification.manager import NotificationUsageManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class NotificationUsageService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.noti_usage_mgr: NotificationUsageManager = self.locator.get_manager('NotificationUsageManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['protocol_id', 'domain_id'])
    def list(self, params):
        """ List Notification Usages

        Args:
            params (dict): {
                'protocol_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)',
            }

        Returns:
            results (list): 'list of user_channel_vo'
            total_count (int)
        """

        query = params.get('query', {})
        return self.noti_usage_mgr.list_notification_usages(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'user_self': 'str', // from meta
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """

        query = params.get('query', {})
        return self.noti_usage_mgr.stat_notification_usages(query)
