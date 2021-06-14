import factory
from spaceone.notification.model.schedule_model import Schedule


class ScheduleFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Schedule

    day_of_week = ['MON', 'WED', 'FRI']
    start_hour = 8
    end_hour = 23