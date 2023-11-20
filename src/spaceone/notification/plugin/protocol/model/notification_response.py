from typing import List, Union
from enum import Enum
from pydantic import BaseModel

__all__ = ['PluginResponse', 'ResourceResponse']

from spaceone.notification.plugin.protocol.model.message import Message


class NotificationType(str, Enum):
    info = 'INFO'
    error = 'ERROR'
    success = 'SUCCESS'
    warning = 'WARNING'


class ResourceType(str, Enum):
    error = 'notification.ErrorResource'


class PluginMetadata(BaseModel):
    filter_format: List[str] = []
    options_schema: dict = {}


class PluginResponse(BaseModel):
    metadata: PluginMetadata


class ResourceResponse(BaseModel):
    notification_type: NotificationType
    message: Message = None
    error_message: str = ''

    class Config:
        use_enum_values = True