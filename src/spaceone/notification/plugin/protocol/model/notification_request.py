from typing import Union
from pydantic import BaseModel

__all__ = ['NotificationDispatchRequest']


class NotificationDispatchRequest(BaseModel):
    options: dict
    secret_data: dict
    channel_data: dict
    message: dict
    notification_type: str
    domain_id: Union[str, None] = None
