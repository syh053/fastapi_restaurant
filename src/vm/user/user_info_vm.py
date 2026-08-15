from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.vm.comment.comment_vm import CommentCreateReqModel
from src.vm.end.restaurant_vm import EndRestaurantRespModel


class UserInfoReqModel(BaseModel):
    id: Annotated[UUID, Field(description='使用者 ID')]
    name: Annotated[str, Field(description='使用者姓名')]
    email: Annotated[str, Field(max_length=256, description='email')]
    is_admin: Annotated[bool, Field(description='是否為管理員')]
    restaurants: list[EndRestaurantRespModel]
    comments_total: int

    model_config = ConfigDict(from_attributes=True)
