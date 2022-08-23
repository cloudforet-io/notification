import logging
import datetime

from spaceone.core import queue, utils
from spaceone.core.service import *
from spaceone.notification.lib.schedule import *
from spaceone.notification.manager import IdentityManager
from spaceone.notification.manager import NotificationManager
from spaceone.notification.manager import ProjectChannelManager
from spaceone.notification.manager import UserChannelManager
from spaceone.notification.manager import ProtocolManager
from spaceone.notification.manager import SecretManager
from spaceone.notification.manager import PluginManager
from spaceone.notification.manager import QuotaManager
from spaceone.notification.manager import NotificationUsageManager
from spaceone.notification.conf.global_conf import *

_LOGGER = logging.getLogger(__name__)
OLD_NOTIFICATION_DAYS = 60


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
        message = params['message']

        domain_info = identity_mgr.get_domain_info(domain_id)
        message['domain_name'] = self.get_domain_name(domain_info)

        identity_mgr.get_resource(resource_id, resource_type, domain_id)

        if resource_type == 'identity.Domain':
            self.dispatch_domain(params)

        elif resource_type == 'identity.Project':
            self.dispatch_project_channel(params)

        elif resource_type == 'identity.User':
            self.dispatch_user_channel(params)

    def dispatch_domain(self, params):
        _LOGGER.debug(f'[Dispatch Domain] Domain ID: {params["resource_id"]}')

        identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
        users = identity_mgr.get_all_users_in_domain(params['resource_id'])

        for user in users:
            user_channel_params = {
                'notification_type': params.get('notification_type', 'INFO'),
                'notification_level': params.get('notification_level', 'ALL'),
                'topic': params['topic'],
                'message': params['message'],
                'resource_type': 'identity.User',
                'resource_id': user['user_id'],
                'domain_id': params['resource_id']
            }

            self.dispatch_user_channel(user_channel_params)

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
            {'filter': [{'k': 'project_id', 'v': resource_id, 'o': 'eq'},
                        {'k': 'domain_id', 'v': domain_id, 'o': 'eq'}]})

        for prj_ch_vo in prj_ch_vos:
            if prj_ch_vo.state == 'ENABLED':
                protocol_vo = protocol_mgr.get_protocol(prj_ch_vo.protocol_id, domain_id)

                dispatch_subscribe = self.check_subscribe_for_dispatch(prj_ch_vo.is_subscribe, prj_ch_vo.subscriptions,
                                                                       topic)
                dispatch_schedule = self.check_schedule_for_dispatch(prj_ch_vo.is_scheduled, prj_ch_vo.schedule)
                dispatch_notification_level = self.check_notification_level_for_dispatch(notification_level,
                                                                                         prj_ch_vo.notification_level)

                _LOGGER.debug(f'[Notification] subscribe: {dispatch_subscribe} | schedule: {dispatch_schedule} '
                              f'| notification_level: {dispatch_notification_level}')

                if dispatch_subscribe and dispatch_schedule and dispatch_notification_level:
                    _LOGGER.info(f'[Notification] Dispatch Notification to project: {resource_id}')

                    if protocol_vo.protocol_type == 'INTERNAL':
                        internal_project_channel_data = prj_ch_vo.data
                        for user_id in internal_project_channel_data.get('users', []):
                            params.update({
                                'resource_type': 'identity.User',
                                'resource_id': user_id
                            })
                            _LOGGER.debug(f'[Forward to User Channel] User ID: {user_id}')
                            self.dispatch_user_channel(params)
                    elif protocol_vo.protocol_type == 'EXTERNAL':
                        _LOGGER.info(f'[Notification] Dispatch Notification to project: {resource_id}')
                        channel_data = self.get_channel_data(prj_ch_vo, protocol_vo, domain_id)
                        secret_data = self.get_secret_data(protocol_vo, domain_id)

                        self.push_queue(protocol_vo.protocol_id, channel_data, secret_data, notification_type, message, domain_id)
                else:
                    _LOGGER.info(f'[Notification] Skip Notification to project: {resource_id}')
            else:
                _LOGGER.info(f'[Notification] Project Channel is disabled: {prj_ch_vo.project_channel_id}')

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
            {'filter': [{'k': 'user_id', 'v': resource_id, 'o': 'eq'},
                        {'k': 'domain_id', 'v': domain_id, 'o': 'eq'}]})

        for user_ch_vo in user_ch_vos:
            if user_ch_vo.state == 'ENABLED':
                protocol_vo = protocol_mgr.get_protocol(user_ch_vo.protocol_id, domain_id)

                dispatch_subscribe = self.check_subscribe_for_dispatch(user_ch_vo.is_subscribe,
                                                                       user_ch_vo.subscriptions, topic)
                dispatch_schedule = self.check_schedule_for_dispatch(user_ch_vo.is_scheduled, user_ch_vo.schedule)

                _LOGGER.debug(f'[Notification] subscribe: {dispatch_subscribe} | schedule: {dispatch_schedule}')

                if dispatch_subscribe and dispatch_schedule:
                    _LOGGER.info(f'[Notification] Dispatch Notification to user: {resource_id}')
                    channel_data = self.get_channel_data(user_ch_vo, protocol_vo, domain_id)
                    secret_data = self.get_secret_data(protocol_vo, domain_id)

                    self.push_queue(protocol_vo.protocol_id, channel_data, secret_data, notification_type, message, domain_id)
                else:
                    _LOGGER.info(f'[Notification] Skip Notification to user: {resource_id}')
            else:
                _LOGGER.info(f'[Notification] User Channel is disabled: {user_ch_vo.user_channel_id}')

        params.update({'user_id': resource_id})
        self.notification_mgr.create_notification(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['protocol_id', 'data', 'message', 'domain_id'])
    def push(self, params):
        """ Push notification

        Args:
            params (dict): {
                'protocol_id': 'str',
                'data': 'str',
                'message': 'dict',
                'notification_type', 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """
        domain_id = params['domain_id']
        protocol_id = params['protocol_id']
        notification_type = params.get('notification_type', 'INFO')
        data = params['data']
        message = params.get('message', {})

        protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')
        protocol_vo = protocol_mgr.get_protocol(protocol_id, domain_id)
        secret_data = self.get_secret_data(protocol_vo, domain_id)

        self.push_queue(protocol_vo.protocol_id, data, secret_data, notification_type, message, domain_id)

    @transaction(append_meta={'authorization.scope': 'USER'})
    @check_required(['notifications', 'domain_id'])
    def delete(self, params):
        """ Delete notifications

        Args:
            params (dict): {
                'notifications': 'list',
                'domain_id': 'str'
            }

        Returns:
            None
        """
        filter_params = {
            'notification_id': params['notifications'],
            'domain_id': params['domain_id']
        }
        notification_vos = self.notification_mgr.filter_notifications(**filter_params)
        self.notification_mgr.delete_notification_by_vos(notification_vos)

    @transaction(append_meta={'authorization.scope': 'USER'})
    @check_required(['notifications', 'domain_id'])
    def set_read(self, params):
        """  Change the notifications to read status.

        Args:
            params (dict): {
                'notifications': 'list',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.notification_mgr.set_read_notification(params['notifications'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'USER'})
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

        return self.notification_mgr.get_notification(params['notification_id'], params['domain_id'],
                                                      params.get('only'))

    @transaction(append_meta={'authorization.scope': 'USER'})
    @check_required(['domain_id'])
    @append_query_filter(['notification_id', 'topic', 'notification_type', 'notification_level', 'is_read',
                          'project_id', 'user_id', 'domain_id', 'user_self'])
    @append_keyword_filter(['notification_id', 'topic'])
    def list(self, params):
        """ List User Channels

        Args:
            params (dict): {
                'notification_id': 'str',
                'topic': 'str',
                'notification_type': 'str',
                'notification_level': 'str',
                'is_read': 'bool',
                'project_id': 'str',
                'user_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of user_channel_vo'
            total_count (int)
        """

        query = params.get('query', {})
        return self.notification_mgr.list_notifications(query)

    @transaction(append_meta={'authorization.scope': 'USER'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id', 'user_self'])
    @append_keyword_filter(['notification_id', 'topic'])
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
        return self.notification_mgr.stat_notifications(query)

    def push_queue(self, protocol_id, channel_data, secret_data, notification_type, message, domain_id):
        task = {
            'name': 'dispatch_notification',
            'version': 'v1',
            'executionEngine': 'BaseWorker',
            'stages': [{
                'locator': 'SERVICE',
                'name': 'NotificationService',
                'metadata': self.transaction.meta,
                'method': 'dispatch_notification',
                'params': {
                    'protocol_id': protocol_id,
                    'channel_data': channel_data,
                    'secret_data': secret_data,
                    'notification_type': notification_type,
                    'message': message,
                    'domain_id': domain_id,
                }
            }]
        }

        _LOGGER.debug(f'[push_queue] task: {task}')
        queue.put('notification_q', utils.dump_json(task))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    def delete_old_notifications(self, params):
        """ Delete old notifications

        Args:
            params (dict): {}

        Returns:
            None
        """
        now = datetime.datetime.now()
        now = now.replace(hour=0, minute=0, second=0, microsecond=0)
        condition_date = now - datetime.timedelta(days=OLD_NOTIFICATION_DAYS)
        condition_date_iso = utils.datetime_to_iso8601(condition_date)

        query = {'filter': [{'k': 'created_at', 'v': condition_date_iso, 'o': 'datetime_lte'}]}
        _LOGGER.debug(f"[delete_old_notifications] Query: {query}")

        notification_vos, total_count = self.notification_mgr.list_notifications(query)

        _LOGGER.debug(f"[delete_old_notifications] Old Notification Count: {total_count}")
        notification_vos.delete()

    def get_channel_data(self, channel_vo, protocol_vo, domain_id):
        secret_mgr: SecretManager = self.locator.get_manager('SecretManager')

        channel_data = None
        plugin_info = protocol_vo.plugin_info.to_dict()
        plugin_metadata = plugin_info.get('metadata', {})

        if plugin_metadata.get('data_type') == 'PLAIN_TEXT':
            channel_data = channel_vo.data
        elif plugin_metadata.get('data_type') == 'SECRET':
            channel_data = secret_mgr.get_secret_data(channel_vo.secret_id, domain_id)

        return channel_data

    def get_secret_data(self, protocol_vo, domain_id):
        secret_mgr: SecretManager = self.locator.get_manager('SecretManager')

        secret_data = {}
        plugin_info = protocol_vo.plugin_info.to_dict()

        if secret_id := plugin_info.get('secret_id'):
            secret_data = secret_mgr.get_secret_data(secret_id, domain_id)

        return secret_data

    def dispatch_notification(self, protocol_id, channel_data, secret_data, notification_type, message, domain_id):
        protocol_mgr: ProtocolManager = self.locator.get_manager('ProtocolManager')
        plugin_mgr: PluginManager = self.locator.get_manager('PluginManager')

        protocol_vo = protocol_mgr.get_protocol(protocol_id, domain_id)

        if protocol_vo.state == 'ENABLED':
            plugin_info = protocol_vo.plugin_info.to_dict()
            options = plugin_info.get('options', {})

            _LOGGER.debug(f'[Plugin Initialize] plugin_id: {plugin_info["plugin_id"]} | version: {plugin_info["version"]} '
                          f'| domain_id: {domain_id}')
            try:
                endpoint_info = plugin_mgr.initialize(plugin_info, domain_id)
                plugin_metadata = plugin_mgr.init_plugin(options)
                plugin_info['metadata'] = plugin_metadata

                if version := endpoint_info.get('updated_version'):
                    plugin_info['version'] = version

                protocol_mgr = self.locator.get_manager('ProtocolManager')
                protocol_mgr.update_protocol_by_vo({'plugin_info': plugin_info}, protocol_vo)

            except Exception as e:
                _LOGGER.error(f'[Notification] Plugin Error: {e}')

            self._dispatch_notification(protocol_vo, secret_data, channel_data, notification_type,
                                        message, options, plugin_mgr)

        else:
            _LOGGER.info('[Notification] Protocol is disabled. skip notification')

    def _dispatch_notification(self, protocol_vo, secret_data, channel_data, notification_type, message, options, plugin_mgr):
        month, date = self.get_month_date()
        noti_usage_vo, usage_month, usage_date = self.get_notification_usage(protocol_vo, month, date)

        try:
            self.check_quota(protocol_vo, usage_month, usage_date)
            plugin_mgr.dispatch_notification(secret_data, channel_data, notification_type, message, options)
            self.increment_usage(noti_usage_vo)
        except Exception as e:
            self.increment_fail_count(noti_usage_vo)

    def check_quota(self, protocol_vo, usage_month, usage_date, count=1):
        quota_mgr: QuotaManager = self.locator.get_manager('QuotaManager')

        query = {'filter': [{'k': 'protocol', 'v': protocol_vo, 'o': 'eq'}]}
        quota_results, quota_total_count = quota_mgr.list_quotas(query)

        if quota_total_count:
            limit = quota_results[0].limit
            self._check_quota_limit(protocol_vo.protocol_id, limit, usage_month, usage_date, count)
        else:
            # Check Default Quota
            plugin_id = protocol_vo.plugin_info.plugin_id

            if plugin_id in DEFAULT_QUOTA:
                limit = DEFAULT_QUOTA[plugin_id]
                self._check_quota_limit(protocol_vo.protocol_id, limit, usage_month, usage_date, count)

    def increment_usage(self, noti_usage_vo, count=1):
        noti_usage_mgr: NotificationUsageManager = self.locator.get_manager('NotificationUsageManager')
        _LOGGER.debug(f"[increment_usage] Incremental Usage Count - Protocol {noti_usage_vo.protocol_id} (count: {count})")
        noti_usage_mgr.incremental_notification_usage(noti_usage_vo, count)

    def increment_fail_count(self, noti_usage_vo, count=1):
        noti_usage_mgr: NotificationUsageManager = self.locator.get_manager('NotificationUsageManager')
        _LOGGER.debug(
            f"[increment_fail_count] Incremental Fail Count - Protocol {noti_usage_vo.protocol_id} (count: {count})")
        noti_usage_mgr.incremental_notification_fail_count(noti_usage_vo, count)

    def get_notification_usage(self, protocol_vo, month, date):
        usage_month = 0
        usage_date = 0
        noti_usage_vo = None

        noti_usage_mgr: NotificationUsageManager = self.locator.get_manager('NotificationUsageManager')

        month_query = {
            'filter': [
                {'k': 'protocol_id', 'v': protocol_vo.protocol_id, 'o': 'eq'},
                {'k': 'usage_month', 'v': month, 'o': 'eq'}
            ]
        }
        month_usage_results, month_usage_total_count = noti_usage_mgr.list_notification_usages(month_query)

        for _noti_usage in month_usage_results:
            usage_month += _noti_usage.count
            if _noti_usage.usage_date == date:
                usage_date = _noti_usage.count
                noti_usage_vo = _noti_usage

        if not noti_usage_vo:
            params = {
                'protocol_id': protocol_vo.protocol_id,
                'usage_month': month,
                'usage_date': date,
                'domain_id': protocol_vo.domain_id
            }
            noti_usage_vo = noti_usage_mgr.create_notification_usage(params)

        return noti_usage_vo, usage_month, usage_date

    @staticmethod
    def check_schedule_for_dispatch(is_scheduled, schedule):
        if is_scheduled:
            now_time = datetime.datetime.utcnow()

            valid_weekday = check_weekday_schedule(now_time, schedule.day_of_week)
            valid_time = check_time_schedule(now_time, schedule.start_hour, schedule.end_hour)

            _LOGGER.debug(f'Weekday: {valid_weekday} | Time {valid_time}')

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
        if notification_level == 'ALL':
            return True
        elif prj_channel_notification_level == notification_level:
            return True

        return False

    @staticmethod
    def get_month_date():
        now = datetime.datetime.now()
        return now.strftime('%Y-%m'), now.strftime('%d')

    @staticmethod
    def _check_quota_limit(protocol_id, limit, usage_month, usage_date, count):
        if 'month' in limit:
            if limit['month'] != -1 and limit['month'] < (usage_month + count):
                raise ERROR_QUOTA_IS_EXCEEDED(protocol_id=protocol_id,
                                              limit=f'limit.month=({usage_month}/{limit["month"]})')

        if 'day' in limit:
            if limit['day'] != -1 and limit['day'] < (usage_date + count):
                raise ERROR_QUOTA_IS_EXCEEDED(protocol_id=protocol_id,
                                              limit=f'limit.day=({usage_date}/{limit["day"]})')

    @staticmethod
    def get_domain_name(domain_info):
        _tags = domain_info.get('tags', {})
        if description := _tags.get('description'):
            return description
        else:
            return domain_info['name']
