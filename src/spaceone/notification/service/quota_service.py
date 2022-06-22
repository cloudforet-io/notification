import logging
import functools

from spaceone.core.service import *
from spaceone.notification.error import *
from spaceone.notification.manager import ProtocolManager
from spaceone.notification.manager import QuotaManager
from spaceone.notification.model import Quota


_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class QuotaService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quota_mgr: QuotaManager = self.locator.get_manager('QuotaManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['protocol_id', 'limit', 'domain_id'])
    def create(self, params):
        """ Create Quota

        Args:
            params (dict): {
                'protocol_id': 'str',
                'limit': 'dict',
                'domain_id': 'str'
            }

        Returns:
            quota_vo (object)
        """
        protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')
        params.update({
            'protocol': protocol_mgr.get_protocol(params['protocol_id'], params['domain_id']),
            'limit': self.limit_validation_check(params['limit'])
        })

        return self.quota_mgr.create_quota(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['quota_id', 'limit', 'domain_id'])
    def update(self, params):
        """ Update Quota

        Args:
            params (dict): {
                'quota_id': 'str',
                'limit': 'dict',
                'domain_id': 'str'
            }

        Returns:
            quota_vo (object)
        """
        quota_vo = self.quota_mgr.get_quota(params['quota_id'], params['domain_id'])

        params['limit'] = self.limit_validation_check(params['limit'])
        return self.quota_mgr.update_quota_by_vo(params, quota_vo)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['quota_id', 'domain_id'])
    def delete(self, params):
        """ Delete Quota

        Args:
            params (dict): {
                'quota_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """
        quota_vo: Quota = self.quota_mgr.get_quota(params['quota_id'], params['domain_id'])
        return self.quota_mgr.delete_quota_by_vo(quota_vo)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['quota_id', 'domain_id'])
    def get(self, params):
        """ Get Quota

        Args:
            params (dict): {
                'quota_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            quota_vo (object)
        """
        return self.quota_mgr.get_quota(params['quota_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['quota_id', 'protocol_id',  'domain_id'])
    def list(self, params):
        """ List Quotas

        Args:
            params (dict): {
                'quota_id': 'str',
                'protocol_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of quota_vo'
            total_count (int)
        """
        query = params.get('query', {})
        return self.quota_mgr.list_quotas(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """

        query = params.get('query', {})
        return self.quota_mgr.stat_quotas(query)

    @staticmethod
    def limit_validation_check(limit):
        valid_limit = {}

        if 'day' in limit:
            if isinstance(limit['day'], int) or isinstance(limit['day'], float):
                if limit['day'] < -1:
                    raise ERROR_QUOTA_LIMIT_TYPE(limit=limit['day'])
            else:
                raise ERROR_QUOTA_LIMIT_TYPE(limit=limit['day'])

            valid_limit['day'] = int(limit['day'])

        if 'month' in limit:
            if isinstance(int(limit['month']), int) or isinstance(int(limit['month']), float):
                if limit['month'] < -1:
                    raise ERROR_QUOTA_LIMIT_TYPE(limit=limit['month'])
            else:
                raise ERROR_QUOTA_LIMIT_TYPE(limit=limit['month'])

            valid_limit['month'] = int(limit['month'])

        return valid_limit
