from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.notification.model.schedule_model import Schedule


class UserChannel(MongoModel):
    user_channel_id = StringField(max_length=40, generate_id="user-ch", unique=True)
    user_id = StringField(max_length=255)
    protocol_id = StringField(max_length=40)
    name = StringField(max_length=255)
    state = StringField(
        max_length=20, default="ENABLED", choices=("ENABLED", "DISABLED")
    )
    data = DictField()
    is_subscribe = BooleanField(default=False)
    subscriptions = ListField(StringField(max_length=255), default=[])
    is_scheduled = BooleanField(default=False)
    schedule = EmbeddedDocumentField(Schedule, default=None, null=True)
    tags = DictField()
    user_secret_id = StringField(max_length=255)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": [
            "name",
            "state",
            "data",
            "is_subscribe",
            "subscriptions",
            "notification_level",
            "is_scheduled",
            "schedule",
            "tags",
        ],
        "minimal_fields": [
            "user_channel_id",
            "name",
            "state",
        ],
        "ordering": ["name"],
        "indexes": [
            # 'user_channel_id',
            "protocol_id",
            "state",
            "tags",
        ],
    }
