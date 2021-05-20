from spaceone.core.service import *

from spaceone.notification.manager import ProtocolManager
from spaceone.notification.model import Protocol


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProtocolService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'plugin_info', 'domain_id'])
    def create(self, params):
        """ Create Protocol

        Args:
            params (dict): {
                'name': 'str',
                'plugin_info': 'dict',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            protocol_vo (object)
        """

        # Create Protocol
        protocol_vo: Protocol = self.protocol_mgr.create_protocol(params)

        return protocol_vo

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['protocol_id', 'domain_id'])
    def update(self, params):
        """ Update protocol

        Args:
            params (dict): {
                'protocol_id': 'str',
                'name': 'str',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            protocol_vo (object)
        """

        return self.protocol_mgr.update_protocol(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['protocol_id', 'domain_id'])
    def delete(self, params):
        """ Delete protocol

        Args:
            params (dict): {
                'protocol_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.protocol_mgr.delete_protocol(params['protocol_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['protocol_id', 'domain_id'])
    def enable(self, params):
        """ Enable protocol

        Args:
            params (dict): {
                'protocol_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            protocol_vo (object)
        """

        return self.protocol_mgr.enable_protocol(params['protocol_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['protocol_id', 'domain_id'])
    def disable(self, params):
        """ Disable protocol

        Args:
            params (dict): {
                'protocol_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            protocol_vo (object)
        """

        return self.protocol_mgr.disable_protocol(params['protocol_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['protocol_id', 'domain_id'])
    def get(self, params):
        """ Disable domain

        Args:
            params (dict): {
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            domain_vo (object)
        """

        return self.protocol_mgr.get_protocol(params['protocol_id'], params['domain_id'], params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['protocol_id', 'name', 'state', 'protocol_type', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['protocol_id'])
    def list(self, params):
        """ List protocol

        Args:
            params (dict): {
                'protocol_id': 'str',
                'name': 'str',
                'state': 'str',
                'protocol_type',
                'query': 'dict (spaceone.api.core.v1.Query)',
                'domain_id': 'str'
            }

        Returns:
            results (list): 'list of protocol_vo'
            total_count (int)
        """

        query = params.get('query', {})
        return self.protocol_mgr.list_protocols(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['protocol_id', 'name'])
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
        return self.protocol_mgr.stat_protocols(query)
