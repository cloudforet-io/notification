from mongoengine import *
from datetime import datetime
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class Schedule(EmbeddedDocument):
    day_of_week = ListField(StringField(choices=['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'], required=True))
    start_hour = IntField(required=True, default=0)
    end_hour = IntField(required=True)


class ProjectChannel(MongoModel):
    project_channel_id = StringField(max_length=40, generate_id='project-ch', unique=True)
    project_id = StringField(max_length=255)
    protocol_id = StringField(max_length=40)
    name = StringField(max_length=255)
    state = StringField(max_length=20, default='ENABLED')
    schema = StringField(max_length=40)
    data = DictField()
    is_subscribe = BooleanField(default=False)
    subscriptions = ListField(StringField(max_length=255))
    notification_level = StringField(default='ALL', max_length=40)
    schedule = EmbeddedDocumentField(Schedule, default=None, null=True)
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
            'schedule',
            'tags'
        ],
        'change_query_keys': {
            'user_projects': 'project_id'
        },
        'minimal_fields': [
            'project_channel_id',
            'name',
            'state',
        ],
        'ordering': ['name'],
        'indexes': [
            'project_channel_id',
            'protocol_id',
            'state',
            'tags'
        ]
    }

