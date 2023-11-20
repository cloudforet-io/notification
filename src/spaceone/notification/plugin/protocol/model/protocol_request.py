from typing import Union
from pydantic import BaseModel

__all__ = ['ProtocolInitRequest', 'ProtocolVerifyRequest']


class ProtocolInitRequest(BaseModel):
    options: dict
    domain_id: Union[str, None] = None


class ProtocolVerifyRequest(BaseModel):
    options: dict
    secret_data: dict
    domain_id: Union[str, None] = None
