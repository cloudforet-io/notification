from typing import Literal
from pydantic import BaseModel, Field

__all__ = ['PluginResponse']

DataType = Literal['PLAIN_TEXT', 'SECRET']


class PluginDataSchema(BaseModel):
    schema_name: dict = Field(alias='schema')


class PluginMetadata(BaseModel):
    data_type: DataType
    data: PluginDataSchema


class PluginResponse(BaseModel):
    metadata: PluginMetadata
