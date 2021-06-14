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
        topic = params['topic']

        resource_type = params['resource_type']
        resource_id = params['resource_id']

        notification_type = params.get('notification_type', 'INFO')
        notification_level = params.get('notification_level', 'ALL')
        message = params['message']

        identity_mgr.get_resource(resource_id, resource_type, domain_id)

        if resource_type == 'identity.Project':
            project_ch_mgr: ProjectChannelManager = self.locator.get_manager('ProjectChannelManager')
            prj_ch_vos, prj_ch_total_count = project_ch_mgr.list_project_channels(
                {'filter': [{'k': 'project_id', 'v': resource_id, 'o': 'eq'}]})

            for prj_ch_vo in prj_ch_vos:
                dispatch_subscribe = self.check_subscribe_for_dispatch(prj_ch_vo.is_subscribe, prj_ch_vo.subscriptions,
                                                                       topic)
                dispatch_schedule = self.check_schedule_for_dispatch(prj_ch_vo.is_scheduled, prj_ch_vo.schedule)
                dispatch_notification_level = self.check_notification_level_for_dispatch(notification_level,
                                                                                         prj_ch_vo.notification_level)

                if dispatch_subscribe and dispatch_schedule and dispatch_notification_level:
                    _LOGGER.info('[Notification] Dispatch Notificaiton to project')
                    self.dispatch_notification(prj_ch_vo, notification_type, message, domain_id)
                else:
                    _LOGGER.info('[Notification] Skip Notificaiton to project')

        elif resource_type == 'identity.User':
            user_ch_mgr: UserChannelManager = self.locator.get_manager('UserChannelManager')
            user_ch_vos, user_ch_total_count = user_ch_mgr.list_user_channels(
                {'filter': [{'k': 'user_id', 'v': resource_id, 'o': 'eq'}]})

            for user_ch_vo in user_ch_vos:
                dispatch_subscribe = self.check_subscribe_for_dispatch(user_ch_vo.is_subscribe,
                                                                       user_ch_vo.subscriptions, topic)
                dispatch_schedule = self.check_schedule_for_dispatch(user_ch_vo.is_scheduled, user_ch_vo.schedule)

                if dispatch_subscribe and dispatch_schedule:
                    _LOGGER.info('[Notification] Dispatch Notificaiton to user')
                    self.dispatch_notification(user_ch_vo, notification_type, message, domain_id)
                else:
                    _LOGGER.info('[Notification] Skip Notificaiton to user')

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

    def dispatch_notification(self, channel_vo, notification_type, message, domain_id):
        protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')
        plugin_mgr: PluginManager = self.locator.get_manager('PluginManager')

        protocol_vo = protocol_mgr.get_protocol(channel_vo.protocol_id, domain_id)
        capability = protocol_vo.capability
        plugin_info = protocol_vo.plugin_info
        secret_data = {}

        if capability['data_type'] == 'PLAIN_TEXT':
            secret_data = channel_vo.data
        elif capability['data_type'] == 'SECRET':
            secret_mgr: SecretManager = self.locator.get_manager('SecretManager')
            secret_data = secret_mgr.get_plugin_secret_data(channel_vo.secret_id, capability['supported_schema'],
                                                            domain_id)

        plugin_mgr.dispatch_notification(secret_data, notification_type, message, plugin_info.options)

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
