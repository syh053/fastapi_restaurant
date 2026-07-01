import uuid
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class EndRestaurantGetReqModel(BaseModel):
    name: Annotated[str | None, Field(description='餐廳名稱')] = None
    category_name: Annotated[str | None, Field(description='餐廳分類')] = None
    tel: Annotated[str | None, Field(description='餐廳電話')] = None
    openingHours: Annotated[int | None, Field(description='餐廳營業時長')] = None
    address: Annotated[str | None, Field(description='餐廳營業時長')] = None
    description: Annotated[str | None, Field(description='備註')] = None
    current_page: Annotated[int, Field(description='目前分頁')] = 0
    page_size: Annotated[int, Field(description='分頁大小')] = 10


class EndRestaurantRespModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[uuid.UUID, Field(description='餐廳名稱')]
    name: Annotated[str, Field(description='餐廳名稱')]
    tel: Annotated[str | None, Field(default=None, description='餐廳電話')]
    openingHours: Annotated[int, Field(description='餐廳營業時長')]
    address: Annotated[str, Field(description='餐廳地址')]
    description: Annotated[str | None, Field(default=None, description='備註')]
    image: Annotated[str | None, Field(default=None, description='圖片')]
    category_id: Annotated[uuid.UUID | None, Field(default=None, description='餐廳分類')]
    category_name: Annotated[str | None, Field(default=None, description='餐廳分類')]


class EndRestaurantReqModel(BaseModel):
    name: str = Field(description='餐廳名稱')
    tel: str | None = Field(default=None, description='餐廳電話')
    openingHours: int = Field(description='餐廳營業時長')
    address: str = Field(description='餐廳地址')
    description: str | None = Field(default=None, description='備註')
    category_id: uuid.UUID | None = Field(default=None, description='餐廳分類')
