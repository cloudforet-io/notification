import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.model.mongo_model import MongoModel
from spaceone.core.transaction import Transaction

from spaceone.notification.service.project_channel_service import ProjectChannelService
from spaceone.notification.model.project_channel_model import ProjectChannel
from spaceone.notification.connector.secret_connector import SecretConnector
from spaceone.notification.connector.identity_connector import IdentityConnector
from spaceone.notification.info.project_channel_info import *
from spaceone.notification.info.common_info import StatisticsInfo
from test.factory.protocol_factory import ProtocolFactory
from test.factory.project_channel_factory import ProjectChannelFactory


class TestProjectChannelService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.notification')
        connect('test', host='mongomock://localhost')

        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'notificaiton',
            'api_class': 'ProjectChannel'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    @patch.object(MongoModel, 'connect', return_value=None)
    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all Project Channel')
        project_channel_vos = ProjectChannel.objects.filter()
        project_channel_vos.delete()

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, 'get_project', return_value={'project_id': 'project-xyz', 'name': 'Project X'})
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_project_channel(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        protocol_id = protocol_vo.protocol_id

        params = {
            'name': 'Test Project Channel',
            'protocol_id': protocol_id,
            'project_id': 'project-xyz',
            'data': {
                'phone_number': '01071700000'
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
        prj_ch_svc = ProjectChannelService(transaction=self.transaction)
        project_ch_vo = prj_ch_svc.create(params.copy())

        print_data(project_ch_vo.to_dict(), 'test_create_project_channel')
        ProjectChannelInfo(project_ch_vo)

        self.assertIsInstance(project_ch_vo, ProjectChannel)
        self.assertEqual(params['name'], project_ch_vo.name)
        self.assertEqual(True, project_ch_vo.is_scheduled)
        self.assertEqual(False, project_ch_vo.is_subscribe)
        self.assertEqual(None, project_ch_vo.secret_id)
        self.assertEqual(params['schedule']['day_of_week'], project_ch_vo.schedule.day_of_week)
        self.assertEqual(params['schedule']['start_hour'], project_ch_vo.schedule.start_hour)
        self.assertEqual(params['tags'], project_ch_vo.tags)
        self.assertEqual(params['domain_id'], project_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, 'get_project', return_value={'project_id': 'project-xyz', 'name': 'Project X'})
    @patch.object(SecretConnector, 'create_secret', return_value={'secret_id': 'secret-xyz', 'name': 'Secret'})
    @patch.object(SecretConnector, 'update_secret', return_value={'secret_id': 'secret-xyz', 'name': 'Update Secret'})
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_project_channel_2(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        protocol_id = protocol_vo.protocol_id

        params = {
            'name': 'Test Project Channel',
            'protocol_id': protocol_id,
            'project_id': 'project-xyz',
            'data': {
                'phone_number': '0101123344'
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
        prj_ch_svc = ProjectChannelService(transaction=self.transaction)
        project_ch_vo = prj_ch_svc.create(params.copy())

        print_data(project_ch_vo.to_dict(), 'test_create_project_channel')
        ProjectChannelInfo(project_ch_vo)

        self.assertIsInstance(project_ch_vo, ProjectChannel)
        self.assertEqual(params['name'], project_ch_vo.name)
        self.assertEqual(True, project_ch_vo.is_scheduled)
        self.assertEqual(False, project_ch_vo.is_subscribe)
        self.assertEqual(None, project_ch_vo.secret_id)
        self.assertEqual(params['schedule']['day_of_week'], project_ch_vo.schedule.day_of_week)
        self.assertEqual(params['schedule']['start_hour'], project_ch_vo.schedule.start_hour)
        self.assertEqual(params['tags'], project_ch_vo.tags)
        self.assertEqual(params['domain_id'], project_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_update_project_channel(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        project_channel_vo = ProjectChannelFactory(protocol_id=protocol_vo.protocol_id, domain_id=self.domain_id)

        name = 'Update Project Channel'
        data = {
            'phone_number': '0109993333'
        }

        params = {
            'name': name,
            'project_channel_id': project_channel_vo.project_channel_id,
            'data': data,
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        prj_ch_svc = ProjectChannelService(transaction=self.transaction)
        update_project_ch_vo = prj_ch_svc.update(params.copy())

        print_data(update_project_ch_vo.to_dict(), 'test_update_project_channel')
        ProjectChannelInfo(update_project_ch_vo)

        self.assertIsInstance(update_project_ch_vo, ProjectChannel)
        self.assertEqual(name, update_project_ch_vo.name)
        self.assertEqual(data, update_project_ch_vo.data)
        self.assertEqual(params['tags'], update_project_ch_vo.tags)
        self.assertEqual(params['domain_id'], update_project_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(SecretConnector, 'update_secret_data')
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_update_project_channel_secret(self, *args):
        protocol_vo = ProtocolFactory(domain_id=self.domain_id)
        project_channel_vo = ProjectChannelFactory(protocol_id=protocol_vo.protocol_id,
                                                   domain_id=self.domain_id,
                                                   secret_id='secret-xyz')
        name = 'Update Project Channel'
        data = {
           'phone_number': '0109994444'
        }

        params = {
            'name': name,
            'project_channel_id': project_channel_vo.project_channel_id,
            'data': data,
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        prj_ch_svc = ProjectChannelService(transaction=self.transaction)
        update_project_ch_vo = prj_ch_svc.update(params.copy())

        print_data(update_project_ch_vo.to_dict(), 'test_update_project_channel')
        ProjectChannelInfo(update_project_ch_vo)

        self.assertIsInstance(update_project_ch_vo, ProjectChannel)
        self.assertEqual(name, update_project_ch_vo.name)
        self.assertEqual('secret-xyz', update_project_ch_vo.secret_id)
        self.assertEqual({}, update_project_ch_vo.data)
        self.assertEqual(params['tags'], update_project_ch_vo.tags)
        self.assertEqual(params['domain_id'], update_project_ch_vo.domain_id)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_set_schedule(self, *args):
        project_channel_vo = ProjectChannelFactory(domain_id=self.domain_id, secret_id='secret-xyz',
                                                   is_scheduled=False, schedule=None)

        schedule = {
            'day_of_week': ['MON', 'TUE'],
            'start_hour': 1,
            'end_hour': 23
        }

        params = {
            'project_channel_id': project_channel_vo.project_channel_id,
            'is_scheduled': True,
            'schedule': schedule,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'set_schedule'
        prj_ch_svc = ProjectChannelService(transaction=self.transaction)
        schedule_project_ch_vo = prj_ch_svc.set_schedule(params.copy())

        print_data(schedule_project_ch_vo.to_dict(), 'test_set_schedule')
        ProjectChannelInfo(schedule_project_ch_vo)

        self.assertIsInstance(schedule_project_ch_vo, ProjectChannel)
        self.assertEqual(schedule_project_ch_vo.is_scheduled, True)
        self.assertEqual(schedule['day_of_week'], schedule_project_ch_vo.schedule.day_of_week)
        self.assertEqual(schedule['start_hour'], schedule_project_ch_vo.schedule.start_hour)
        self.assertEqual(schedule['end_hour'], schedule_project_ch_vo.schedule.end_hour)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_set_subscription(self, *args):
        project_channel_vo = ProjectChannelFactory(domain_id=self.domain_id, secret_id='secret-xyz',
                                                   is_subscribe=False, subscriptions=[])
        subscriptions = ['a', 'b', 'c']

        params = {
            'project_channel_id': project_channel_vo.project_channel_id,
            'is_subscribe': True,
            'subscriptions': subscriptions,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'set_schedule'
        prj_ch_svc = ProjectChannelService(transaction=self.transaction)
        subscription_project_ch_vo = prj_ch_svc.set_schedule(params.copy())

        print_data(subscription_project_ch_vo.to_dict(), 'test_set_subscription')
        ProjectChannelInfo(subscription_project_ch_vo)

        self.assertIsInstance(subscription_project_ch_vo, ProjectChannel)
        self.assertEqual(subscription_project_ch_vo.is_subscribe, True)
        self.assertEqual(subscriptions, subscription_project_ch_vo.subscriptions)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_enable_project_channel(self, *args):
        project_channel_vo = ProjectChannelFactory(domain_id=self.domain_id, state='DISABLED')
        params = {
            'project_channel_id': project_channel_vo.project_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'enable'
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        updated_project_channel_vo = project_channel_svc.enable(params.copy())

        print_data(updated_project_channel_vo.to_dict(), 'test_enable_project_channel')
        ProjectChannelInfo(updated_project_channel_vo)

        self.assertIsInstance(updated_project_channel_vo, ProjectChannel)
        self.assertEqual(updated_project_channel_vo.project_channel_id, project_channel_vo.project_channel_id)
        self.assertEqual('ENABLED', updated_project_channel_vo.state)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_disable_project_channel(self, *args):
        project_channel_vo = ProjectChannelFactory(domain_id=self.domain_id, state='ENABLED')
        params = {
            'project_channel_id': project_channel_vo.project_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'disable'
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        updated_project_channel_vo = project_channel_svc.disable(params.copy())

        print_data(updated_project_channel_vo.to_dict(), 'test_disable_project_channel')
        ProjectChannelInfo(updated_project_channel_vo)

        self.assertIsInstance(updated_project_channel_vo, ProjectChannel)
        self.assertEqual(updated_project_channel_vo.project_channel_id, project_channel_vo.project_channel_id)
        self.assertEqual('DISABLED', updated_project_channel_vo.state)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_delete_project_channel(self, *args):
        project_channel_vo = ProjectChannelFactory(domain_id=self.domain_id)
        params = {
            'project_channel_id': project_channel_vo.project_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        result = project_channel_svc.delete(params)

        self.assertIsNone(result)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(SecretConnector, 'delete_secret')
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_delete_user_channel_secret(self, *args):
        project_channel_vo = ProjectChannelFactory(domain_id=self.domain_id, secret_id='secret-abcde')
        params = {
            'project_channel_id': project_channel_vo.project_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        result = project_channel_svc.delete(params)

        self.assertIsNone(result)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_get_project_channel(self, *args):
        project_channel_vo = ProjectChannelFactory(domain_id=self.domain_id)
        params = {
            'project_channel_id': project_channel_vo.project_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        get_project_channel_vo = project_channel_svc.get(params)

        print_data(get_project_channel_vo.to_dict(), 'test_get_project_channel')
        ProjectChannelInfo(get_project_channel_vo)

        self.assertIsInstance(get_project_channel_vo, ProjectChannel)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_project_channels_by_project_channel_id(self, *args):
        project_channel_vos = ProjectChannelFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), project_channel_vos))

        params = {
            'project_channel_id': project_channel_vos[0].project_channel_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'list'
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        project_channel_vos, total_count = project_channel_svc.list(params)
        ProjectChannelsInfo(project_channel_vos, total_count)

        self.assertEqual(len(project_channel_vos), 1)
        self.assertIsInstance(project_channel_vos[0], ProjectChannel)
        self.assertEqual(total_count, 1)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_project_channels_by_name(self, *args):
        project_channel_vos = ProjectChannelFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), project_channel_vos))

        params = {
            'name': project_channel_vos[0].name,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'list'
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        project_channel_vos, total_count = project_channel_svc.list(params)
        ProjectChannelsInfo(project_channel_vos, total_count)

        self.assertEqual(len(project_channel_vos), 1)
        self.assertIsInstance(project_channel_vos[0], ProjectChannel)
        self.assertEqual(total_count, 1)

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_project_channel(self, *args):
        project_channel_vos = ProjectChannelFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), project_channel_vos))

        params = {
            'domain_id': self.domain_id,
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'project_channel_id',
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
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        values = project_channel_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_project_channel')

    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(IdentityConnector, '__init__', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_project_channel_distinct(self, *args):
        project_channel_vos = ProjectChannelFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), project_channel_vos))

        params = {
            'domain_id': self.domain_id,
            'query': {
                'distinct': 'project_channel_id',
                'page': {
                    'start': 2,
                    'limit': 3
                }
            }
        }

        self.transaction.method = 'stat'
        project_channel_svc = ProjectChannelService(transaction=self.transaction)
        values = project_channel_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_project_channel_distinct')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)