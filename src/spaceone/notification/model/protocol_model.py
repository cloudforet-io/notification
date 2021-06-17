from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class PluginInfo(EmbeddedDocument):
    plugin_id = StringField(max_length=40)
    version = StringField(max_length=255)
    options = DictField(default={})
    metadata = DictField(default={})
    secret_id = StringField(max_length=40)
    schema = StringField(max_length=255)


class Protocol(MongoModel):
    protocol_id = StringField(max_length=40, generate_id='protocol', unique=True)
    name = StringField(max_length=255)
    state = StringField(max_length=20, default='ENABLED', choices=('ENABLED', 'DISABLED'))
    protocol_type = StringField(max_length=40, default='EXTERNAL', choices=('EXTERNAL', 'INTERNAL'))
    resource_type = StringField(max_length=40, null=True, default=None)
    capability = DictField()
    plugin_info = EmbeddedDocumentField(PluginInfo, default={})
    tags = DictField()
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'state',
            'plugin_info',
            'tags'
        ],
        'minimal_fields': [
            'protocol_id',
            'name',
            'state',
        ],
        'ordering': ['name'],
        'indexes': [
            'protocol_id',
            'state',
            'tags'
        ]
    }
