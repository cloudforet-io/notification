import factory

from spaceone.core import utils
from spaceone.notification.model.user_channel_model import UserChannel
from .schedule_factory import ScheduleFactory


class UserChannelFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = UserChannel

    user_channel_id = factory.LazyAttribute(lambda o: utils.generate_id('user-ch'))
    protocol_id = utils.generate_id('protocol')
    name = factory.LazyAttribute(lambda o: utils.random_string())

    state = 'ENABLED'
    schema = 'slack_webhook'
    data = {
        'token': utils.random_string(),
        'channel': 'everyone'
    }
    is_subscribe = True
    subscriptions = ['topic-a', 'topic-b']
    is_scheduled = True

    schedule = factory.SubFactory(ScheduleFactory)

    tags = {
        'xxx': 'yy'
    }

    domain_id = utils.generate_id('domain')
    user_id = utils.generate_id('user')
    created_at = factory.Faker('date_time')

