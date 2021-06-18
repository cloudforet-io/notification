from spaceone.notification.error import *

def validate_json_schema(schema, data):
    for required_key in schema.get('required', []):
        if required_key not in data:
            raise ERROR_REQUIRED_PARAMETER(key=f'data.{required_key}')

    # TODO: Check Properties
