import factory

from spaceone.core import utils
from spaceone.notification.model.notification_model import Notification


class NotificationFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Notification

    notification_id = factory.LazyAttribute(lambda o: utils.generate_id('notification'))
    topic = 'topic-a'
    message = {
        'message': 'This is TC..'
    }
    notification_type = 'ERROR'
    notification_level = 'ALL'
    is_read = False
    user_id = utils.generate_id('user')
    domain_id = utils.generate_id('domain')
    created_at = factory.Faker('date_time')
