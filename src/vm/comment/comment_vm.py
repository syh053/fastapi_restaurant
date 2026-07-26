import uuid
from typing import Annotated

from pydantic import Field, BaseModel


class CommentCreateReqModel(BaseModel):
    text: Annotated[str, Field(max_length=300, description='餐廳評論')]
    restaurant_id: Annotated[uuid.UUID, Field(description='餐廳 ID')]

