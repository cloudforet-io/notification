import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.model.mongo_model import MongoModel
from spaceone.core.transaction import Transaction
from spaceone.notification.service.notification_service import NotificationService
from spaceone.notification.manager.secret_manager import SecretManager
from spaceone.notification.model.notification_model import Notification
from spaceone.notification.manager.plugin_manager import PluginManager
from spaceone.notification.manager.identity_manager import IdentityManager

from spaceone.notification.info.notification_info import *
from spaceone.notification.info.common_info import StatisticsInfo
from test.factory.notification_factory import NotificationFactory
from test.factory.protocol_factory import ProtocolFactory
from test.factory.project_channel_factory import ProjectChannelFactory
from test.factory.user_channel_factory import UserChannelFactory
from test.factory.quota_factory import QuotaFactory
from test.factory.notification_usage_factory import NotificationUsageFactory


class TestProtocolService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.notification')
        config.set_service_config()
        config.set_global(MOCK_MODE=True)
        connect('test', host='mongomock://localhost')

        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'notification',
            'api_class': 'Notification'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    @patch.object(MongoModel, 'connect', return_value=None)
    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all notification')
        notification_vos = Notification.objects.filter()
        notification_vos.delete()

    @patch.object(IdentityManager, 'get_resource', return_value={})
    def test_create_notification_without_channel(self, *args):
        project_id = utils.generate_id('project')

        params = {
            'resource_type': 'identity.Project',
            'resource_id': project_id,
            'topic': 'topic-a',
            'message': {
                'message': 'TEST..'
            },
            'notification_type': 'ERROR',
            'notification_level': 'ALL',
            'domain_id': self.domain_id,
        }

        self.transaction.method = 'create'
        notification_svc = NotificationService(transaction=self.transaction)
        notification_svc.create(params.copy())

    @patch.object(IdentityManager, 'get_resource', return_value={})
    @patch.object(SecretManager, 'get_secret_data', return_value={'data': {'xxxx': 'yyyy'}})
    @patch.object(PluginManager, 'dispatch_notification', return_value=None)
    def test_create_notification_with_project_channel(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        project_channel_vo = ProjectChannelFactory(domain_id=self.domain_id, protocol_id=protocol_vo.protocol_id)

        params = {
            'resource_type': 'identity.Project',
            'resource_id': project_channel_vo.project_id,
            'topic': 'topic-a',
            'message': {
                'message': 'TEST..'
            },
            'notification_type': 'ERROR',
            'notification_level': 'LV1',
            'domain_id': self.domain_id,
        }

        self.transaction.method = 'create'
        notification_svc = NotificationService(transaction=self.transaction)
        notification_svc.create(params.copy())

    @patch.object(IdentityManager, 'get_resource', return_value={})
    @patch.object(SecretManager, 'get_secret_data', return_value={'data': {'xxxx': 'yyyy'}})
    @patch.object(PluginManager, 'dispatch_notification', return_value=None)
    def test_create_notification_with_user_channel(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id, protocol_id=protocol_vo.protocol_id)

        params = {
            'resource_type': 'identity.User',
            'resource_id': user_channel_vo.user_id,
            'topic': 'topic-a',
            'message': {
                'message': 'TEST..'
            },
            'notification_type': 'ERROR',
            'notification_level': 'ALL',
            'domain_id': self.domain_id,
        }

        self.transaction.method = 'create'
        notification_svc = NotificationService(transaction=self.transaction)
        notification_svc.create(params.copy())

    @patch.object(SecretManager, 'get_secret_data', return_value={'data': {'xxxx': 'yyyy'}})
    @patch.object(PluginManager, 'dispatch_notification', return_value=None)
    def test_push_notification(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        QuotaFactory(protocol=protocol_vo, protocol_id=protocol_vo.protocol_id, domain_id=self.domain_id)
        NotificationUsageFactory(protocol_id=protocol_vo.protocol_id, domain_id=self.domain_id, usage_date='01')
        noti_usage_vo = NotificationUsageFactory(protocol_id=protocol_vo.protocol_id, domain_id=self.domain_id)

        params = {
            'protocol_id': protocol_vo.protocol_id,
            'data': '',
            'message': {
                'message': 'TEST..'
            },
            'notification_type': 'ERROR',
            'domain_id': self.domain_id,
        }

        self.transaction.method = 'push'
        notification_svc = NotificationService(transaction=self.transaction)
        notification_svc.push(params.copy())

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_delete_notification(self, *args):
        notification_vo = NotificationFactory(domain_id=self.domain_id)

        params = {
            'notification_id': notification_vo.notification_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        notification_svc = NotificationService(transaction=self.transaction)
        result = notification_svc.delete(params)

        self.assertIsNone(result)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_get_notification(self, *args):
        notification_vo = NotificationFactory(domain_id=self.domain_id)

        params = {
            'notification_id': notification_vo.notification_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        notification_svc = NotificationService(transaction=self.transaction)
        get_noti_vo = notification_svc.get(params)

        print_data(get_noti_vo.to_dict(), 'test_get_notification')
        NotificationInfo(get_noti_vo)

        self.assertIsInstance(get_noti_vo, Notification)
        self.assertEqual(get_noti_vo.notification_id, notification_vo.notification_id)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_delete_all_notifications(self, *args):
        notification_vos = NotificationFactory.build_batch(20, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), notification_vos))

        user_ids = [notification_vo.user_id for notification_vo in notification_vos]

        params = {
            'users': user_ids[:10],
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete_all'
        notification_svc = NotificationService(transaction=self.transaction)
        notification_svc.delete_all(params)

        notification_vos, total_count = notification_svc.list({'domain_id': self.domain_id})
        self.assertEqual(total_count, 10)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_set_read_notification(self, *args):
        notification_vos = NotificationFactory.build_batch(20, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), notification_vos))

        notification_ids = [notification_vo.notification_id for notification_vo in notification_vos]

        params = {
            'notifications': notification_ids[:10],
            'domain_id': self.domain_id
        }

        self.transaction.method = 'set_read'
        notification_svc = NotificationService(transaction=self.transaction)
        notification_svc.set_read(params)

        params = {
            'is_read': True,
            'domain_id': self.domain_id
        }

        read_notification_vos, total_count = notification_svc.list(params)

        self.assertIsInstance(read_notification_vos[0], Notification)
        self.assertEqual(total_count, 10)
        self.assertEqual(read_notification_vos[0].is_read, True)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_notifications_by_notification_id(self, *args):
        notification_vos = NotificationFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), notification_vos))

        params = {
            'notification_id': notification_vos[0].notification_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'list'
        notification_svc = NotificationService(transaction=self.transaction)
        notification_vos, total_count = notification_svc.list(params)
        NotificationsInfo(notification_vos, total_count)

        self.assertEqual(len(notification_vos), 1)
        self.assertIsInstance(notification_vos[0], Notification)
        self.assertEqual(total_count, 1)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_notifications_by_name(self, *args):
        notification_topic_x_vos = NotificationFactory.build_batch(10, topic='topic-x', domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), notification_topic_x_vos))

        notification_topic_y_vos = NotificationFactory.build_batch(5, topic='topic-y', domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), notification_topic_y_vos))

        params = {
            'topic': 'topic-y',
            'domain_id': self.domain_id
        }

        self.transaction.method = 'list'
        notification_svc = NotificationService(transaction=self.transaction)
        list_result_notification_vos, total_count = notification_svc.list(params)
        NotificationsInfo(list_result_notification_vos, total_count)

        self.assertEqual(len(list_result_notification_vos), 5)
        self.assertIsInstance(list_result_notification_vos[0], Notification)
        self.assertEqual(total_count, 5)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_notifications_by_notification_type(self, *args):
        success_noti_vos = NotificationFactory.build_batch(5, notification_type='SUCCESS', domain_id=self.domain_id)
        error_noti_vos = NotificationFactory.build_batch(10, notification_type='ERROR', domain_id=self.domain_id)
        warn_noti_vos = NotificationFactory.build_batch(20, notification_type='WARNING', domain_id=self.domain_id)

        list(map(lambda vo: vo.save(), success_noti_vos))
        list(map(lambda vo: vo.save(), error_noti_vos))
        list(map(lambda vo: vo.save(), warn_noti_vos))

        params = {
            'notification_type': 'ERROR',
            'domain_id': self.domain_id
        }

        self.transaction.method = 'list'
        notification_svc = NotificationService(transaction=self.transaction)
        list_result_notification_vos, total_count = notification_svc.list(params)
        NotificationsInfo(list_result_notification_vos, total_count)

        self.assertEqual(len(list_result_notification_vos), 10)
        self.assertIsInstance(list_result_notification_vos[0], Notification)
        self.assertEqual(total_count, 10)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_notification(self, *args):
        notification_vos = NotificationFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), notification_vos))

        params = {
            'domain_id': self.domain_id,
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'notification_id',
                            'name': 'Id'
                        }],
                        'fields': [{
                            'operator': 'count',
                            'name': 'Count'
                        }]
                    }
                }, {
                    'sort': {
                        'key': 'Count',
                        'desc': True
                    }
                }]
            }
        }

        self.transaction.method = 'stat'
        noti_svc = NotificationService(transaction=self.transaction)
        values = noti_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_notification')

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_notification_distinct(self, *args):
        notification_vos = NotificationFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), notification_vos))

        params = {
            'domain_id': self.domain_id,
            'query': {
                'distinct': 'notification_id',
                'page': {
                    'start': 2,
                    'limit': 3
                }
            }
        }

        self.transaction.method = 'stat'
        notification_svc = NotificationService(transaction=self.transaction)
        values = notification_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_notification_distinct')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)