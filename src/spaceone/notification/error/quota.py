from spaceone.core.error import *


class ERROR_QUOTA_LIMIT_TYPE(ERROR_BASE):
    _message = '{limit} is invalid type.'


class ERROR_QUOTA_IS_EXCEEDED(ERROR_BASE):
    _message = 'Dispatch a notification is not possible because the quota is exceeded. ' \
               '(Protocol={protocol_id}, {limit})'
