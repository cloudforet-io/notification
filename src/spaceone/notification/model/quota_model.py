from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.notification.model.protocol_model import Protocol


class Quota(MongoModel):
    quota_id = StringField(max_length=40, generate_id='quota', unique=True)
    protocol = ReferenceField('Protocol', reverse_delete_rule=DO_NOTHING)
    protocol_id = StringField(max_length=40)
    limit = DictField(default={})
    domain_id = StringField(max_length=40)

    meta = {
        'updatable_fields': [
            'limit'
        ],
        'minimal_fields': [
            'quota_id',
            'protocol_id',
            'domain_id',
        ],
        'ordering': ['quota_id'],
        'indexes': [
            # 'quota_id',
            'protocol_id',
            'domain_id'
        ]
    }
