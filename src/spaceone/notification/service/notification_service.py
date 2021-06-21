import logging
from datetime import datetime

from spaceone.core.service import *
from spaceone.notification.lib.schedule import *
from spaceone.notification.manager import IdentityManager
from spaceone.notification.manager import NotificationManager
from spaceone.notification.manager import ProjectChannelManager
from spaceone.notification.manager import UserChannelManager
from spaceone.notification.manager import ProtocolManager
from spaceone.notification.manager import SecretManager
from spaceone.notification.manager import PluginManager


_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class NotificationService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_mgr: NotificationManager = self.locator.get_manager('NotificationManager')

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
                'notification_type': 'str' -> INFO(default) | ERROR | SUCCESS | WARNING,
                'notification_level': 'str' -> ALL(default) | LV1 | LV2 | LV3 | LV4 | LV5,
                'domain_id': 'str'
            }

        Returns:
            notification_vo (object)
        """
        identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')

        domain_id = params['domain_id']
        resource_type = params['resource_type']
        resource_id = params['resource_id']

        identity_mgr.get_resource(resource_id, resource_type, domain_id)

        if resource_type == 'identity.Project':
            self.dispatch_project_channel(params)

        elif resource_type == 'identity.User':
            self.dispatch_user_channel(params)

    def dispatch_project_channel(self, params):
        _LOGGER.debug(f'[Dispatch Project Channel] Project ID: {params["resource_id"]}')
        protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')
        project_ch_mgr: ProjectChannelManager = self.locator.get_manager('ProjectChannelManager')

        domain_id = params['domain_id']
        topic = params['topic']
        resource_id = params['resource_id']

        notification_type = params.get('notification_type', 'INFO')
        notification_level = params.get('notification_level', 'ALL')
        message = params['message']

        prj_ch_vos, prj_ch_total_count = project_ch_mgr.list_project_channels(
            {'filter': [{'k': 'project_id', 'v': resource_id, 'o': 'eq'}]})

        internal_project_channel = None
        for prj_ch_vo in prj_ch_vos:
            if prj_ch_vo.state == 'ENABLED':
                protocol_vo = protocol_mgr.get_protocol(prj_ch_vo.protocol_id, domain_id)

                if protocol_vo.protocol_type == 'INTERNAL':
                    internal_project_channel = prj_ch_vo
                elif protocol_vo.protocol_type == 'EXTERNAL':
                    dispatch_subscribe = self.check_subscribe_for_dispatch(prj_ch_vo.is_subscribe, prj_ch_vo.subscriptions,
                                                                           topic)
                    dispatch_schedule = self.check_schedule_for_dispatch(prj_ch_vo.is_scheduled, prj_ch_vo.schedule)
                    dispatch_notification_level = self.check_notification_level_for_dispatch(notification_level,
                                                                                             prj_ch_vo.notification_level)

                    _LOGGER.debug(f'[Notification] subscribe: {dispatch_subscribe} | schedule: {dispatch_schedule} '
                                  f'| notification_level: {dispatch_notification_level}')

                    if dispatch_subscribe and dispatch_schedule and dispatch_notification_level:
                        _LOGGER.info(f'[Notification] Dispatch Notification to project: {resource_id}')
                        self.dispatch_notification(protocol_vo, prj_ch_vo, notification_type, message, domain_id)
                    else:
                        _LOGGER.info(f'[Notification] Skip Notification to project: {resource_id}')
            else:
                _LOGGER.info(f'[Notification] Project Channel is disabled: {prj_ch_vo.project_channel_id}')

        if internal_project_channel:
            internal_project_channel_data = internal_project_channel.data
            for user_id in internal_project_channel_data.get('users', []):
                params.update({
                    'resource_type': 'identity.User',
                    'resource_id': user_id
                })
                _LOGGER.debug(f'[Forward to User Channel] User ID: {user_id}')
                self.dispatch_user_channel(params)

    def dispatch_user_channel(self, params):
        _LOGGER.debug(f'[Dispatch User Channel] User ID: {params["resource_id"]}')

        protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')
        user_ch_mgr: UserChannelManager = self.locator.get_manager('UserChannelManager')

        domain_id = params['domain_id']
        topic = params['topic']
        resource_id = params['resource_id']

        notification_type = params.get('notification_type', 'INFO')
        message = params['message']

        user_ch_vos, user_ch_total_count = user_ch_mgr.list_user_channels(
            {'filter': [{'k': 'user_id', 'v': resource_id, 'o': 'eq'}]})

        for user_ch_vo in user_ch_vos:
            if user_ch_vo.state == 'ENABLED':
                protocol_vo = protocol_mgr.get_protocol(user_ch_vo.protocol_id, domain_id)

                dispatch_subscribe = self.check_subscribe_for_dispatch(user_ch_vo.is_subscribe,
                                                                       user_ch_vo.subscriptions, topic)
                dispatch_schedule = self.check_schedule_for_dispatch(user_ch_vo.is_scheduled, user_ch_vo.schedule)

                if dispatch_subscribe and dispatch_schedule:
                    _LOGGER.info(f'[Notification] Dispatch Notification to user: {resource_id}')
                    self.dispatch_notification(protocol_vo, user_ch_vo, notification_type, message, domain_id)
                else:
                    _LOGGER.info(f'[Notification] Skip Notification to user: {resource_id}')
            else:
                _LOGGER.info(f'[Notification] User Channel is disabled: {user_ch_vo.project_channel_id}')

        params.update({'user_id': resource_id})
        self.notification_mgr.create_notification(params)

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
                'only': 'list',
                'set_read': 'bool'
            }

        Returns:
            notification_vo (object)
        """

        notification_vo = self.notification_mgr.get_notification(params['notification_id'], params['domain_id'],
                                                                 params.get('only'))

        if params.get('set_read', False) and notification_vo.is_read is False:
            self.notification_mgr.set_read_notification(notification_vo)

        return notification_vo

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['notification_id', 'topic', 'notification_type', 'notification_level', 'parent_notification_id', 'project_id', 'user_id', 'domain_id'])
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
                'set_read': 'bool',
                'query': 'dict (spaceone.api.core.v1.Query)',
                'domain_id': 'str'
            }

        Returns:
            results (list): 'list of user_channel_vo'
            total_count (int)
        """

        query = params.get('query', {})
        notification_vos, total_count = self.notification_mgr.list_notifications(query)

        # TODO: update is_read when set_read is True
        return notification_vos, total_count

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

    def dispatch_notification(self, protocol_vo, channel_vo, notification_type, message, domain_id):
        plugin_mgr: PluginManager = self.locator.get_manager('PluginManager')
        secret_mgr: SecretManager = self.locator.get_manager('SecretManager')

        if protocol_vo.state == 'ENABLED':
            plugin_info = protocol_vo.plugin_info
            secret_data = {}
            channel_data = {}

            if secret_id := plugin_info.secret_id:
                secret_data = secret_mgr.get_secret_data(secret_id, domain_id)

            if plugin_info.metadata['data_type'] == 'PLAIN_TEXT':
                channel_data = channel_vo.data
            elif plugin_info.metadata['data_type'] == 'SECRET':
                channel_data = secret_mgr.get_secret_data(channel_vo.secret_id, domain_id)

            _LOGGER.debug(f'[Plugin Initialize] plugin_id: {plugin_info.plugin_id} | version: {plugin_info.version}')

            plugin_mgr.initialize(plugin_info.plugin_id, plugin_info.version, domain_id)
            plugin_mgr.dispatch_notification(secret_data, channel_data, notification_type, message, plugin_info.options)
        else:
            _LOGGER.info('[Notification] Protocol is disabled. skip notification')

    @staticmethod
    def check_schedule_for_dispatch(is_scheduled, schedule):
        if is_scheduled:
            now_time = datetime.now(tz=None)    # UTC

            valid_weekday = check_weekday_schedule(now_time, schedule.day_of_week)
            valid_time = check_time_schedule(now_time, schedule.start_hour, schedule.end_hour)

            if valid_weekday and valid_time:
                return True
        else:
            return True

        return False

    @staticmethod
    def check_subscribe_for_dispatch(is_subscribe, subscriptions, topic):
        if is_subscribe is False:
            return True
        elif is_subscribe and topic in subscriptions:
            return True

        return False

    @staticmethod
    def check_notification_level_for_dispatch(notification_level, prj_channel_notification_level):
        if prj_channel_notification_level == 'ALL' or notification_level == 'ALL':
            return True
        elif prj_channel_notification_level == notification_level:
            return True

        return False
