import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.model.mongo_model import MongoModel
from spaceone.core.transaction import Transaction

from spaceone.notification.service.user_channel_service import UserChannelService
from spaceone.notification.model.user_channel_model import UserChannel
from spaceone.notification.connector.secret_connector import SecretConnector
from spaceone.notification.connector.identity_connector import IdentityConnector
from spaceone.notification.info.user_channel_info import *
from spaceone.notification.info.common_info import StatisticsInfo
from test.factory.protocol_factory import ProtocolFactory
from test.factory.user_channel_factory import UserChannelFactory


class TestUserChannelService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.notification')
        connect('test', host='mongomock://localhost')

        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'notificaiton',
            'api_class': 'UserChannel'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    @patch.object(MongoModel, 'connect', return_value=None)
    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all User Channel')
        user_channel_vos = UserChannel.objects.filter()
        user_channel_vos.delete()

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, 'get_user', return_value={'user_id': 'bluese05', 'name': 'JH Song'})
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_user_channel(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        protocol_id = protocol_vo.protocol_id

        params = {
            'name': 'Test User Channel',
            'protocol_id': protocol_id,
            'schema': 'slack_webhook',
            'user_id': 'bluese05',
            'data': {
                'token': 'xxxxxx',
                'channel': 'bob'
            },
            'is_scheduled': True,
            'schedule': {
                'day_of_week': ['MON'],
                'start_hour': 1,
                'end_hour': 10
            },
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        user_ch_svc = UserChannelService(transaction=self.transaction)
        user_ch_vo = user_ch_svc.create(params.copy())

        print_data(user_ch_vo.to_dict(), 'test_create_project_channel')
        UserChannelInfo(user_ch_vo)

        self.assertIsInstance(user_ch_vo, UserChannel)
        self.assertEqual(params['name'], user_ch_vo.name)
        self.assertEqual(True, user_ch_vo.is_scheduled)
        self.assertEqual(False, user_ch_vo.is_subscribe)
        self.assertEqual(None, user_ch_vo.secret_id)
        self.assertEqual(params['schedule']['day_of_week'], user_ch_vo.schedule.day_of_week)
        self.assertEqual(params['schedule']['start_hour'], user_ch_vo.schedule.start_hour)
        self.assertEqual(params['tags'], user_ch_vo.tags)
        self.assertEqual(params['domain_id'], user_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, 'get_user', return_value={'user_id': 'bluese05', 'name': 'JH Song'})
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_user_channel_no_schedule(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        protocol_id = protocol_vo.protocol_id

        params = {
            'name': 'Test User Channel',
            'protocol_id': protocol_id,
            'schema': 'slack_webhook',
            'user_id': 'bluese05',
            'data': {
                'token': 'xxxxxx',
                'channel': 'bob'
            },
            'is_scheduled': False,
            'schedule': None,
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        user_ch_svc = UserChannelService(transaction=self.transaction)
        user_ch_vo = user_ch_svc.create(params.copy())

        print_data(user_ch_vo.to_dict(), 'test_create_project_channel')
        UserChannelInfo(user_ch_vo)

        self.assertIsInstance(user_ch_vo, UserChannel)
        self.assertEqual(params['name'], user_ch_vo.name)
        self.assertEqual(False, user_ch_vo.is_scheduled)
        self.assertEqual(None, user_ch_vo.schedule)
        self.assertEqual(False, user_ch_vo.is_subscribe)
        self.assertEqual(None, user_ch_vo.secret_id)
        self.assertEqual(params['tags'], user_ch_vo.tags)
        self.assertEqual(params['domain_id'], user_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, 'get_user', return_value={'user_id': 'bluese05', 'name': 'JH Song'})
    @patch.object(SecretConnector, 'create_secret', return_value={'secret_id': 'secret-xyz', 'name': 'Secret'})
    @patch.object(SecretConnector, 'update_secret', return_value={'secret_id': 'secret-xyz', 'name': 'Update Secret'})
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_user_channel_secret(self, *args):
        protocol_capability = {
            'data_type': 'SECRET',
            'supported_schema': ['slack_webhook']
        }

        protocol_vo = ProtocolFactory(domain_id=self.domain_id, capability=protocol_capability)
        protocol_id = protocol_vo.protocol_id

        params = {
            'name': 'Test User Channel',
            'protocol_id': protocol_id,
            'schema': 'slack_webhook',
            'user_id': 'bluese05',
            'data': {
                'token': 'xxxxxx',
                'channel': 'bob'
            },
            'is_scheduled': True,
            'schedule': {
                'day_of_week': ['MON'],
                'start_hour': 1,
                'end_hour': 10
            },
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        user_ch_svc = UserChannelService(transaction=self.transaction)
        user_ch_vo = user_ch_svc.create(params.copy())

        print_data(user_ch_vo.to_dict(), 'test_create_project_channel')
        UserChannelInfo(user_ch_vo)

        self.assertIsInstance(user_ch_vo, UserChannel)
        self.assertEqual(params['name'], user_ch_vo.name)
        self.assertEqual(True, user_ch_vo.is_scheduled)
        self.assertEqual(False, user_ch_vo.is_subscribe)
        self.assertEqual('secret-xyz', user_ch_vo.secret_id)
        self.assertEqual({}, user_ch_vo.data)
        self.assertEqual(params['schedule']['day_of_week'], user_ch_vo.schedule.day_of_week)
        self.assertEqual(params['schedule']['start_hour'], user_ch_vo.schedule.start_hour)
        self.assertEqual(params['tags'], user_ch_vo.tags)
        self.assertEqual(params['domain_id'], user_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_update_user_channel(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id)
        name = 'Update User Channel'
        data = {
            'token': 'update-token',
            'channel': 'update-channel'
        }

        params = {
            'name': name,
            'user_channel_id': user_channel_vo.user_channel_id,
            'data': data,
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        user_ch_svc = UserChannelService(transaction=self.transaction)
        update_user_ch_vo = user_ch_svc.update(params.copy())

        print_data(update_user_ch_vo.to_dict(), 'test_update_project_channel')
        UserChannelInfo(update_user_ch_vo)

        self.assertIsInstance(update_user_ch_vo, UserChannel)
        self.assertEqual(name, update_user_ch_vo.name)
        self.assertEqual(data, update_user_ch_vo.data)
        self.assertEqual(params['tags'], update_user_ch_vo.tags)
        self.assertEqual(params['domain_id'], update_user_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(SecretConnector, 'update_secret_data')
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_update_user_channel_secret(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id, secret_id='secret-xyz')
        name = 'Update User Channel'
        data = {
            'token': 'update-token',
            'channel': 'update-channel'
        }

        params = {
            'name': name,
            'user_channel_id': user_channel_vo.user_channel_id,
            'data': data,
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        user_ch_svc = UserChannelService(transaction=self.transaction)
        update_user_ch_vo = user_ch_svc.update(params.copy())

        print_data(update_user_ch_vo.to_dict(), 'test_update_user_channel_secret')
        UserChannelInfo(update_user_ch_vo)

        self.assertIsInstance(update_user_ch_vo, UserChannel)
        self.assertEqual(name, update_user_ch_vo.name)
        self.assertEqual('secret-xyz', update_user_ch_vo.secret_id)
        self.assertEqual({}, update_user_ch_vo.data)
        self.assertEqual(params['tags'], update_user_ch_vo.tags)
        self.assertEqual(params['domain_id'], update_user_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_set_schedule(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id, secret_id='secret-xyz',
                                             is_scheduled=False, schedule=None)

        schedule = {
            'day_of_week': ['MON', 'TUE'],
            'start_hour': 1,
            'end_hour': 23
        }

        params = {
            'user_channel_id': user_channel_vo.user_channel_id,
            'is_scheduled': True,
            'schedule': schedule,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'set_schedule'
        user_ch_svc = UserChannelService(transaction=self.transaction)
        schedule_user_ch_vo = user_ch_svc.set_schedule(params.copy())

        print_data(schedule_user_ch_vo.to_dict(), 'test_set_schedule')
        UserChannelInfo(schedule_user_ch_vo)

        self.assertIsInstance(schedule_user_ch_vo, UserChannel)
        self.assertEqual(schedule_user_ch_vo.is_scheduled, True)
        self.assertEqual(schedule['day_of_week'], schedule_user_ch_vo.schedule.day_of_week)
        self.assertEqual(schedule['start_hour'], schedule_user_ch_vo.schedule.start_hour)
        self.assertEqual(schedule['end_hour'], schedule_user_ch_vo.schedule.end_hour)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_set_subscription(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id, secret_id='secret-xyz',
                                             is_subscribe=False, subscriptions=[])
        subscriptions = ['a', 'b', 'c']

        params = {
            'user_channel_id': user_channel_vo.user_channel_id,
            'is_subscribe': True,
            'subscriptions': subscriptions,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'set_schedule'
        user_ch_svc = UserChannelService(transaction=self.transaction)
        subscription_user_ch_vo = user_ch_svc.set_schedule(params.copy())

        print_data(subscription_user_ch_vo.to_dict(), 'test_set_subscription')
        UserChannelInfo(subscription_user_ch_vo)

        self.assertIsInstance(subscription_user_ch_vo, UserChannel)
        self.assertEqual(subscription_user_ch_vo.is_subscribe, True)
        self.assertEqual(subscriptions, subscription_user_ch_vo.subscriptions)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_enable_user_channel(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id, state='DISABLED')
        params = {
            'user_channel_id': user_channel_vo.user_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'enable'
        user_channel_svc = UserChannelService(transaction=self.transaction)
        updated_user_channel_vo = user_channel_svc.enable(params.copy())

        print_data(updated_user_channel_vo.to_dict(), 'test_enable_user_channel')
        UserChannelInfo(updated_user_channel_vo)

        self.assertIsInstance(updated_user_channel_vo, UserChannel)
        self.assertEqual(updated_user_channel_vo.user_channel_id, user_channel_vo.user_channel_id)
        self.assertEqual('ENABLED', updated_user_channel_vo.state)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_disable_user_channel(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id, state='ENABLED')
        params = {
            'user_channel_id': user_channel_vo.user_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'disable'
        user_channel_svc = UserChannelService(transaction=self.transaction)
        updated_user_channel_vo = user_channel_svc.disable(params.copy())

        print_data(updated_user_channel_vo.to_dict(), 'test_disable_project_channel')
        UserChannelInfo(updated_user_channel_vo)

        self.assertIsInstance(updated_user_channel_vo, UserChannel)
        self.assertEqual(updated_user_channel_vo.user_channel_id, user_channel_vo.user_channel_id)
        self.assertEqual('DISABLED', updated_user_channel_vo.state)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_delete_user_channel(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id)
        params = {
            'user_channel_id': user_channel_vo.user_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        user_channel_svc = UserChannelService(transaction=self.transaction)
        result = user_channel_svc.delete(params)

        self.assertIsNone(result)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(SecretConnector, 'delete_secret')
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_delete_user_channel_secret(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id, secret_id='secret-abcde')
        params = {
            'user_channel_id': user_channel_vo.user_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        user_channel_svc = UserChannelService(transaction=self.transaction)
        result = user_channel_svc.delete(params)

        self.assertIsNone(result)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_get_user_channel(self, *args):
        user_channel_vo = UserChannelFactory(domain_id=self.domain_id)
        params = {
            'user_channel_id': user_channel_vo.user_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        user_channel_svc = UserChannelService(transaction=self.transaction)
        get_user_channel_vo = user_channel_svc.get(params)

        print_data(get_user_channel_vo.to_dict(), 'test_get_user_channel')
        UserChannelInfo(get_user_channel_vo)

        self.assertIsInstance(get_user_channel_vo, UserChannel)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_user_channels_by_user_channel_id(self, *args):
        user_channel_vos = UserChannelFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), user_channel_vos))

        params = {
            'user_channel_id': user_channel_vos[0].user_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'list'
        user_channel_svc = UserChannelService(transaction=self.transaction)
        user_channel_svc, total_count = user_channel_svc.list(params)
        UserChannelsInfo(user_channel_svc, total_count)

        self.assertEqual(len(user_channel_svc), 1)
        self.assertIsInstance(user_channel_svc[0], UserChannel)
        self.assertEqual(total_count, 1)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_user_channels_by_name(self, *args):
        user_channel_vos = UserChannelFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), user_channel_vos))

        params = {
            'name': user_channel_vos[0].name,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'list'
        user_channel_svc = UserChannelService(transaction=self.transaction)
        user_channel_vos, total_count = user_channel_svc.list(params)
        UserChannelsInfo(user_channel_vos, total_count)

        self.assertEqual(len(user_channel_vos), 1)
        self.assertIsInstance(user_channel_vos[0], UserChannel)
        self.assertEqual(total_count, 1)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_user_channel(self, *args):
        user_channel_vos = UserChannelFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), user_channel_vos))

        params = {
            'domain_id': self.domain_id,
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'user_channel_id',
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
        user_channel_svc = UserChannelService(transaction=self.transaction)
        values = user_channel_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_user_channel')

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_user_channel_distinct(self, *args):
        user_channel_vos = UserChannelFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), user_channel_vos))

        params = {
            'domain_id': self.domain_id,
            'query': {
                'distinct': 'user_channel_id',
                'page': {
                    'start': 2,
                    'limit': 3
                }
            }
        }

        self.transaction.method = 'stat'
        user_channel_svc = UserChannelService(transaction=self.transaction)
        values = user_channel_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_user_channel_distinct')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)