from mongoengine import *
from datetime import datetime
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class Schedule(EmbeddedDocument):
    day_of_week = ListField(StringField)
    start_hour = IntField()
    end_hour = IntField()


class Channel(MongoModel):
    protocol_id = StringField(max_length=40)
    name = StringField(max_length=255)
    state = StringField(max_length=20, default='ENABLED')
    schema = StringField(max_length=40)
    data = DictField()
    subscriptions = ListField(StringField(max_length=255))
    notification_level = StringField(max_length=40)
    schedule = EmbeddedDocumentField(Schedule, default=None, null=True)
    tags = DictField()
    secret_id = StringField(max_length=255)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
