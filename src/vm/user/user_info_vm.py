from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.vm.end.restaurant_vm import EndRestaurantRespModel


class UserInfoRespModel(BaseModel):
    id: Annotated[UUID, Field(description='使用者 ID')]
    name: Annotated[str, Field(description='使用者姓名')]
    email: Annotated[str, Field(max_length=256, description='email')]
    image: Annotated[str | None, Field(default=None, description='使用者大頭貼')]
    role: Annotated[str, Field(description='角色')]
    restaurants: list[EndRestaurantRespModel]
    comments_total: int

    model_config = ConfigDict(from_attributes=True)


class UserInfoUpdateReqModel(BaseModel):
    name: Annotated[str | None, Field(default=None, description='使用者名稱')]
    email: Annotated[str | None, Field(default=None, description="使用者信箱")]

    model_config = ConfigDict(from_attributes=True)
