import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class EndUserGetReqModel(BaseModel):
    name: Annotated[str | None, Field(default=None, description="姓名")]
    email: Annotated[str | None, Field(default=None, description="信箱")]
    role: Annotated[Literal["user", "owner", "super_admin"] | None, Field(default=None, description="角色")]
    current_page: Annotated[int, Field(description='目前分頁')] = 0
    page_size: Annotated[int, Field(description='分頁大小')] = 10


class EndUserRespModel(BaseModel):
    id: Annotated[uuid.UUID, Field(description='餐廳名稱')]
    name: Annotated[str, Field(description="姓名")]
    email: Annotated[str, Field(description="信箱")]
    role: Annotated[str, Field(description="角色")]


class EndUserUpdateReqModel(BaseModel):
    id: Annotated[uuid.UUID, Field(description='餐廳名稱')]
    role: Annotated[Literal["user", "owner", "super_admin"], Field(description="角色")]
