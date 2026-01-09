from pydantic import BaseModel
from typing import Optional


class PostMessageRequest(BaseModel):
    message: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    is_point: Optional[bool] = None


class PostMessageResponse(BaseModel):
    response: str
