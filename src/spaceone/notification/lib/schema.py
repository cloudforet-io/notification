from jsonschema import validate
from spaceone.notification.error import *

def validate_json_schema(data, schema):
    try:
        validate(instance=data, schema=schema)
    except Exception as e:
        if e.validator in ['pattern']:
            raise ERROR_JSON_SCHEMA_PATTERN(data=e.instance, schema_title=e.schema["title"])
        else:
            raise ERROR_JSON_SCHEMA(data=e.instance, message=e.message)
