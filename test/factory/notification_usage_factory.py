import factory
import datetime
from spaceone.core import utils
from spaceone.notification.model.notification_usage_model import NotificationUsage

now = datetime.datetime.now()

def get_month():
    return now.strftime('%Y-%m')

def get_date():
    return now.strftime('%d')


class NotificationUsageFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = NotificationUsage

    protocol_id = factory.LazyAttribute(lambda o: utils.generate_id('protocol'))
    usage_month = get_month()
    usage_date = get_date()
    count = 4
    domain_id = utils.generate_id('domain')

