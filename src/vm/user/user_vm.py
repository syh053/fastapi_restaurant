from typing import Annotated

from fastapi import Body
from pydantic import BaseModel, Field


class UserAddReq(BaseModel):
    name: Annotated[str, Body(max_length=128, description='使用者姓名')]
    email: Annotated[str, Body(max_length=256, description='email')]
    password: Annotated[str, Body(max_length=128, description='使用者密碼')]
    confirm_password: Annotated[str, Body(max_length=128, description='確認使用者密碼')]


class UserGetReqModel(BaseModel):
    name: Annotated[str, Body(description='使用者姓名')]
    password: Annotated[str, Body(description='使用者密碼')]


class UserGetRespModel(BaseModel):
    name: Annotated[str, Field(description='使用者姓名')]
    email: Annotated[str, Field(max_length=256, description='email')]
