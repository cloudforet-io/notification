from typing import Union, Literal, List
from pydantic import BaseModel

__all__ = ['NotificationDispatchRequest']

NotificationType = Literal['INFO', 'ERROR', 'SUCCESS', 'WARNING']
ContentType = Literal['HTML', 'MARKDOWN']


class Tag(BaseModel):
    key: str
    value: str
    options: Union[dict, None] = None


class Callback(BaseModel):
    label: str
    url: str
    options: Union[dict, None] = None


class Message(BaseModel):
    title: str
    link: Union[str, None] = None
    description: Union[str, None] = None
    short_description: Union[str, None] = None
    contents: Union[str, None] = None
    content_type: Union[ContentType, None] = None
    image_url: Union[str, None] = None
    tags: Union[List[Tag], None] = None
    callbacks: Union[List[Callback], None] = None
    occurred_at: Union[str, None] = None
    domain_name: Union[str, None] = None


class NotificationDispatchRequest(BaseModel):
    options: dict
    secret_data: dict
    channel_data: dict
    message: Message
    notification_type: NotificationType
    domain_id: Union[str, None] = None
