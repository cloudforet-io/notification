from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Notification(MongoModel):
    notification_id = StringField(max_length=40, generate_id='notification', unique=True)
    topic = StringField(max_length=255)
    message = DictField()
    notification_type = StringField(max_length=20, default='INFO')
    notification_level = StringField(max_length=40, default='ALL')
    is_read = BooleanField(default=False)
    user_id = StringField(max_length=60)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'is_read'
        ],
        'minimal_fields': [
            'notification_id',
            'topic',
            'notification_type',
            'notification_level',
        ],
        'indexes': [
            # 'notification_id',
            'topic',
            'notification_type',
            'notification_level',
            'is_read',
            'user_id',
            'domain_id'
        ]
    }
