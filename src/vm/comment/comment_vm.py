import uuid
from datetime import datetime
from typing import Annotated

from pydantic import Field, BaseModel, ConfigDict


class CommentCreateReqModel(BaseModel):
    text: Annotated[str, Field(max_length=300, description='餐廳評論')]
    restaurant_id: Annotated[uuid.UUID, Field(description='餐廳 ID')]


class CommentGetRespModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    comment_id: Annotated[uuid.UUID, Field(description='評論 ID')]
    restaurant_name: Annotated[str, Field(description='餐廳名稱')]
    user_name: Annotated[str, Field(description='使用者名稱')]
    comment: Annotated[str, Field(description='餐廳評論')]
    created_at: Annotated[datetime, Field(description="建立時間")]
    updated_at: Annotated[datetime, Field(description="修改時間")]
