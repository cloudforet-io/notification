from typing import List, Union
from enum import Enum
from pydantic import BaseModel

__all__ = ['PluginResponse']


class PluginMetadata(BaseModel):
    filter_format: List[str] = []
    options_schema: dict = {}


class PluginResponse(BaseModel):
    metadata: PluginMetadata

