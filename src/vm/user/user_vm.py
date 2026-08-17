from typing import Annotated
from uuid import UUID

from fastapi import Body
from pydantic import BaseModel, Field, ConfigDict


class UserAddReq(BaseModel):
    name: Annotated[str, Body(max_length=128, description='使用者姓名')]
    email: Annotated[str, Body(max_length=256, description='email')]
    password: Annotated[str, Body(max_length=128, description='使用者密碼')]
    confirm_password: Annotated[str, Body(max_length=128, description='確認使用者密碼')]


class UserGetReqModel(BaseModel):
    name: Annotated[str, Body(description='使用者姓名')]
    password: Annotated[str, Body(description='使用者密碼')]


class UserGetRespModel(BaseModel):
    id: Annotated[UUID, Field(description='使用者 ID')]
    name: Annotated[str, Field(description='使用者姓名')]
    email: Annotated[str, Field(max_length=256, description='email')]
    image: Annotated[str | None, Field(default=None, description='使用者大頭貼')]
    password: Annotated[str, Body(description='密碼')]
    is_admin: Annotated[bool, Body(description='是否為管理員')]

    model_config = ConfigDict(from_attributes=True)
