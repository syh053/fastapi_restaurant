from typing import TypeVar, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.model.database import get_session

T = TypeVar("T")

def get_service(service_class: Type[T]):
    def dependency(session: AsyncSession = Depends(get_session)):
        return service_class(session)
    return dependency
