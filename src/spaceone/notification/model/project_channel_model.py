from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.notification.model.schedule_model import Schedule


class ProjectChannel(MongoModel):
    project_channel_id = StringField(
        max_length=40, generate_id="project-ch", unique=True
    )
    name = StringField(max_length=255)
    state = StringField(
        max_length=20, default="ENABLED", choices=("ENABLED", "DISABLED")
    )
    data = DictField()
    is_subscribe = BooleanField(default=False)
    subscriptions = ListField(StringField(max_length=255), default=[])
    notification_level = StringField(
        default="LV1", max_length=40, choices=("LV1", "LV2", "LV3", "LV4", "LV5")
    )
    is_scheduled = BooleanField(default=False)
    schedule = EmbeddedDocumentField(Schedule, default=None, null=True)
    tags = DictField()
    secret_id = StringField(max_length=255)
    protocol_id = StringField(max_length=40)
    project_id = StringField(max_length=255)
    workspace_id = StringField(default=None, null=True, max_length=40)
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
        "change_query_keys": {"user_projects": "project_id"},
        "minimal_fields": [
            "project_channel_id",
            "name",
            "state",
        ],
        "ordering": ["name"],
        "indexes": [
            "state",
            "is_subscribe",
            "is_scheduled",
            "secret_id",
            "protocol_id",
            "project_id",
            "workspace_id",
            "domain_id",
        ],
    }
