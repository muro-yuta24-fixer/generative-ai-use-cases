from pydantic import BaseModel
from typing import List


class UnrecordedMessage(BaseModel):
    role: str
    content: str


class Model(BaseModel):
    modelId: str
    region: str


class StreamingRequest(BaseModel):
    systemPrompt: str
    userPrompt: str
    messages: List[UnrecordedMessage]
    model: Model

