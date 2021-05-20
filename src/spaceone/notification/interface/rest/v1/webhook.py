import logging
from fastapi import APIRouter

_LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
async def webhook(params: dict):
    _LOGGER.debug(f"Request Params: {params}")
    return {"TEST": params}
