from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class PluginInfo(EmbeddedDocument):
    plugin_id = StringField(max_length=255)
    version = StringField(max_length=255)
    options = DictField(default={})
    metadata = DictField(default={})
    secret_id = StringField(max_length=40)
    schema = StringField(max_length=255)
    upgrade_mode = StringField(
        max_length=255, choices=("AUTO", "MANUAL"), default="AUTO"
    )

    def to_dict(self):
        return dict(self.to_mongo())


class Protocol(MongoModel):
    protocol_id = StringField(max_length=40, generate_id="protocol", unique=True)
    name = StringField(max_length=255, unique_with=["domain_id"])
    state = StringField(
        max_length=20, default="ENABLED", choices=("ENABLED", "DISABLED")
    )
    protocol_type = StringField(
        max_length=40, default="EXTERNAL", choices=("EXTERNAL", "INTERNAL")
    )
    resource_type = StringField(max_length=40, null=True, default=None)
    capability = DictField()
    plugin_info = EmbeddedDocumentField(PluginInfo, default={})
    tags = DictField()
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": ["name", "state", "plugin_info", "tags"],
        "minimal_fields": [
            "protocol_id",
            "name",
            "state",
        ],
        "ordering": ["name"],
        "indexes": [
            "state",
            "protocol_type",
            "domain_id",
        ],
    }
