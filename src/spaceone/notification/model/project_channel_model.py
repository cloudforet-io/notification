from mongoengine import *
from datetime import datetime
from spaceone.core.error import *
from spaceone.notification.model.channel_model import Channel


class ProjectChannel(Channel):
    project_channel_id = StringField(max_length=40, generate_id='project-ch', unique=True)
    project_id = StringField(max_length=255)

    meta = {
        'updatable_fields': [
            'name',
            'state',
            'data',
            'subscriptions',
            'notification_level',
            'schedule',
            'tags'
        ],
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

