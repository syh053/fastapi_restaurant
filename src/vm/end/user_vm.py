import uuid
from typing import Annotated

from pydantic import BaseModel, Field


class EndUserGetReqModel(BaseModel):
    name: Annotated[str | None, Field(default=None, description="姓名")]
    email: Annotated[str | None, Field(default=None, description="信箱")]
    is_admin: Annotated[bool | None, Field(default=None, description="是否為管理員")]
    current_page: Annotated[int, Field(description='目前分頁')] = 0
    page_size: Annotated[int, Field(description='分頁大小')] = 10


class EndUserRespModel(BaseModel):
    id: Annotated[uuid.UUID, Field(description='餐廳名稱')]
    name: Annotated[str, Field(description="姓名")]
    email: Annotated[str, Field(description="信箱")]
    is_admin: Annotated[bool, Field(description="是否為管理員")]


class EndUserUpdateReqModel(BaseModel):
    id: Annotated[uuid.UUID, Field(description='餐廳名稱')]
    is_admin: Annotated[bool, Field(description="是否為管理員")]
