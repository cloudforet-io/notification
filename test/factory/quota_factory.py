import factory
from spaceone.core import utils
from spaceone.notification.model.quota_model import Quota, QuotaLimit


class QuotaLimitFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = QuotaLimit

    day = 5
    month = 10


class QuotaFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Quota

    quota_id = factory.LazyAttribute(lambda o: utils.generate_id('quota'))
    limit = factory.SubFactory(QuotaLimitFactory)
    domain_id = utils.generate_id('domain')
    protocol = None
    protocol_id = utils.generate_id('protocol')
