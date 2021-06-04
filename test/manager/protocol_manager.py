import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.model.mongo_model import MongoModel
from spaceone.core.transaction import Transaction
from spaceone.notification.error import *
from spaceone.notification.manager.protocol_manager import ProtocolManager
from spaceone.notification.model.protocol_model import Protocol
from spaceone.notification.info.protocol_info import *
from spaceone.notification.info.common_info import StatisticsInfo
from test.factory.protocol_factory import ProtocolFactory


class TestProtocolManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.notification')
        connect('test', host='mongomock://localhost')

        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'notification',
            'api_class': 'Protocol'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    @patch.object(MongoModel, 'connect', return_value=None)
    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all protocol')
        protocol_vos = Protocol.objects.filter()
        protocol_vos.delete()

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_protocol(self, *args, **kwargs):
        plugin_id = utils.generate_id('plugin')
        plugin_version = '1.0'

        params = {
            'name': 'Slack Protocol',
            'plugin_info': {
                'plugin_id': plugin_id,
                'version': plugin_version,
                'options': {},
            },
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        protocol_mgr = ProtocolManager(transaction=self.transaction)
        protocol_vo = protocol_mgr.create_protocol(params.copy())
        print_data(protocol_vo.to_dict(), 'test_create_protocol')

        self.assertIsInstance(protocol_vo, Protocol)
        self.assertEqual(params['name'], protocol_vo.name)
        self.assertEqual(params['tags'], protocol_vo.tags)
        self.assertEqual(params['domain_id'], protocol_vo.domain_id)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)