from spaceone.core.error import *

class ERROR_PROTOCOL_DISABLED(ERROR_INVALID_ARGUMENT):
    _message = 'Protocol was disabled.'

class ERROR_NOT_SUPPORT_SCHEMA(ERROR_INVALID_ARGUMENT):
    _message = 'Protocol is not supported schema. (schema = {schema})'

class ERROR_WRONG_SCHEDULE_SETTINGS(ERROR_BASE):
    _message = "The schedule format is incorrect. (key = {key})"

class ERROR_WRONG_SCHEDULE_HOURS_SETTINGS(ERROR_BASE):
    _message = "The end hour must be greater than start hour. (start_hour={start_hour}, end_hour={end_hour})"

class ERROR_WRONG_SCHEDULE_DAY(ERROR_BASE):
    _message = "Invalid day to set schedule (day = {day})"
