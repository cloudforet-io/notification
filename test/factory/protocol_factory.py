import factory

from spaceone.core import utils
from spaceone.notification.model.protocol_model import Protocol, PluginInfo


class PluginInfoFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = PluginInfo

    plugin_id = factory.LazyAttribute(lambda o: utils.generate_id('plugin'))
    version = '1.0'
    options = {}
    metadata = {}


class ProtocolFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Protocol

    protocol_id = factory.LazyAttribute(lambda o: utils.generate_id('protocol'))
    name = factory.LazyAttribute(lambda o: utils.random_string())
    state = 'ENABLED'
    protocol_type = 'EXTERNAL'

    resource_type = 'identity.User'
    capability = {
        'data_type': 'SECRET',
        'supported_schema': [
            'slack_webhook'
        ]
    }

    plugin_info = factory.SubFactory(PluginInfoFactory)

    tags = {
        'xxx': 'yy'
    }
    domain_id = utils.generate_id('domain')
    created_at = factory.Faker('date_time')
