from spaceone.notification.error import *

def validate_schedule(schedule):
    if 'day_of_week' not in schedule:
        raise ERROR_REQUIRED_PARAMETER(key='schedule.day_of_week')

    schedule['start_hour'] = schedule.get('start_hour', 0)
    schedule['end_hour'] = schedule.get('end_hour', 0)

    if schedule['start_hour'] < 0 or schedule['start_hour'] > 24:
        raise ERROR_WRONG_SCHEDULE_SETTINGS(key='schedule.start_hour')

    if schedule['end_hour'] < 1 or schedule['end_hour'] > 25:
        raise ERROR_WRONG_SCHEDULE_SETTINGS(key='schedule.end_hour')

    if schedule['start_hour'] == schedule['end_hour']:
        raise ERROR_WRONG_SCHEDULE_SETTINGS(key='schedule.start_hour')

def check_weekday_schedule(now_time, day_of_week):
    DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    week_day = now_time.weekday()

    if DAYS[week_day] in day_of_week:
        return True

    return False

def check_time_schedule(now_time, start_hour, end_hour):
    hour = now_time.hour

    if start_hour < end_hour:
        if start_hour <= hour < end_hour:
            return True
        else:
            return False
    else:
        if start_hour <= hour or hour < end_hour:
            return True
        else:
            return False
