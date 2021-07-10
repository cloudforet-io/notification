import factory

from spaceone.core import utils
from spaceone.notification.model.protocol_model import Protocol, PluginInfo


class PluginInfoFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = PluginInfo

    plugin_id = factory.LazyAttribute(lambda o: utils.generate_id('plugin'))
    version = '1.0'
    options = {}
    metadata = {
        'data_type': 'PLAIN_TEXT',
        'data':  {
            'schema': {
                'properties': {
                    'phone_number': {
                        'minLength': 8,
                        'title': 'Phone Number',
                        'type': 'string',
                        'pattern': '^01(?:0|1|[6-9])(\\d{3}|\\d{4})(\\d{4})$'
                        # 'pattern': '^[0-9.\-]{8,15}$'
                    }
                },
                'required': [
                    'phone_number'
                ],
                'type': 'object'
            }
        }
    }
    secret_id = utils.generate_id('secret')


class ProtocolFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Protocol

    protocol_id = factory.LazyAttribute(lambda o: utils.generate_id('protocol'))
    name = factory.LazyAttribute(lambda o: utils.random_string())
    state = 'ENABLED'
    protocol_type = 'EXTERNAL'

    resource_type = 'identity.User'
    capability = {'supported_schema': ['slack_webhook']}

    plugin_info = factory.SubFactory(PluginInfoFactory)

    tags = {
        'xxx': 'yy'
    }
    domain_id = utils.generate_id('domain')
    created_at = factory.Faker('date_time')
