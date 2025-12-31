from pydantic import BaseModel


class PostMessageRequest(BaseModel):
    message: str


class PostMessageResponse(BaseModel):
    response: str
