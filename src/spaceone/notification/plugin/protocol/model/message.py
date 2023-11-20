import datetime
from typing import List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel

__all__ = ['Message', 'Tag', 'Callback']


class Tag(TypedDict, total=False):
    key: str
    value: str
    options: dict


class Callback(TypedDict, total=False):
    label: str
    url: str
    options: dict


class Message(BaseModel):
    title: str = None
    link: str
    description: str
    short_description: str
    contents: str
    content_type: 'HTML | MARKDOWN'
    image_url: str
    tags: List[Tag] = []
    callbacks: List[Callback] = []
    occurred_at: datetime
    domain_name: str
