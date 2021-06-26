from spaceone.core.error import *


class ERROR_JSON_SCHEMA(ERROR_BASE):
    _message = '{message}. (data={data})'


class ERROR_JSON_SCHEMA_PATTERN(ERROR_BASE):
    _message = 'Data is not matched {schema_title} pattern. (data={data})'
