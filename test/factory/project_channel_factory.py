import factory

from spaceone.core import utils
from spaceone.notification.model.project_channel_model import ProjectChannel
from .schedule_factory import ScheduleFactory


class ProjectChannelFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = ProjectChannel

    project_channel_id = factory.LazyAttribute(lambda o: utils.generate_id('project-ch'))
    protocol_id = utils.generate_id('protocol')
    name = factory.LazyAttribute(lambda o: utils.random_string())

    state = 'ENABLED'
    data = {
        'token': utils.random_string(),
        'channel': 'everyone'
    }
    is_subscribe = True
    subscriptions = ['topic-a', 'topic-b']
    notification_level = 'LV1'
    is_scheduled = True

    schedule = factory.SubFactory(ScheduleFactory)

    tags = {
        'xxx': 'yy'
    }

    domain_id = utils.generate_id('domain')
    project_id = utils.generate_id('project')
    created_at = factory.Faker('date_time')

