from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class NotificationUsage(MongoModel):
    protocol_id = StringField(max_length=40)
    usage_date = StringField(max_length=255)
    usage_month = StringField(max_length=255)
    count = IntField(default=0)
    fail_count = IntField(default=0)
    domain_id = StringField(max_length=255)

    meta = {
        "updatable_fields": ["count", "fail_count"],
        "minimal_fields": [
            "protocol_id",
            "usage_date",
            "usage_month",
            "count",
            "fail_count",
            "domain_id",
        ],
        "ordering": ["protocol_id", "usage_month", "usage_date"],
        "indexes": ["protocol_id", "usage_date", "usage_month", "domain_id"],
    }
