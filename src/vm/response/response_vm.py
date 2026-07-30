from typing import TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None = None