from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Schedule(EmbeddedDocument):
    day_of_week = ListField(StringField(choices=['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'], required=True))
    start_hour = IntField(required=True, default=0)
    end_hour = IntField(required=True)
