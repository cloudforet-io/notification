from typing import Literal
from pydantic import BaseModel, Field

__all__ = ['PluginResponse']

DataType = Literal['PLAIN_TEXT', 'SECRET']


class PluginDataSchema(BaseModel):
    json_schema: dict = Field(alias="schema")

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data['schema'] = data.pop('json_schema')
        return data


class PluginMetadata(BaseModel):
    data_type: DataType
    data: PluginDataSchema


class PluginResponse(BaseModel):
    metadata: PluginMetadata
