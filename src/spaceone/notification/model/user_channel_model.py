from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Schedule(EmbeddedDocument):
    day_of_week = ListField(StringField(choices=['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'], required=True))
    start_hour = IntField(required=True, default=0)
    end_hour = IntField(required=True)


class UserChannel(MongoModel):
    user_channel_id = StringField(max_length=40, generate_id='user-ch', unique=True)
    user_id = StringField(max_length=255)
    protocol_id = StringField(max_length=40)
    name = StringField(max_length=255)
    state = StringField(max_length=20, default='ENABLED')
    schema = StringField(max_length=40)
    data = DictField()
    is_subscribe = BooleanField(default=False)
    subscriptions = ListField(StringField(max_length=255), default=[])
    is_scheduled = BooleanField(default=False)
    schedule = EmbeddedDocumentField(Schedule, default={})
    tags = DictField()
    secret_id = StringField(max_length=255)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'state',
            'data',
            'is_subscribe',
            'subscriptions',
            'notification_level',
            'is_scheduled',
            'schedule',
            'tags'
        ],
        'minimal_fields': [
            'user_channel_id',
            'name',
            'state',
        ],
        'ordering': ['name'],
        'indexes': [
            'user_channel_id',
            'protocol_id',
            'state',
            'tags'
        ]
    }
