from mongoengine import *
from datetime import datetime
from spaceone.core.error import *
from spaceone.notification.model.channel_model import Channel

class UserChannel(Channel):
    user_channel_id = StringField(max_length=40, generate_id='user-ch', unique=True)
    user_id = StringField(max_length=255)

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
