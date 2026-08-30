import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class MenuGetReqModel(BaseModel):
    name: Annotated[str | None, Field(description="餐點名稱")] = None
    section: Annotated[str | None, Field(description="分區")] = None
    restaurant_id: Annotated[uuid.UUID | None, Field(description="餐廳 ID")] = None
    current_page: Annotated[int, Field(description="目前分頁")] = 0
    page_size: Annotated[int, Field(description="分頁大小")] = 10


class MenuRespModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[uuid.UUID, Field(description="菜單項目 ID")]
    restaurant_id: Annotated[uuid.UUID | None, Field(default=None, description="餐廳 ID")]
    restaurant_name: Annotated[str | None, Field(default=None, description="餐廳名稱")]
    name: Annotated[str, Field(description="餐點名稱")]
    price: Annotated[int, Field(description="價格")]
    section: Annotated[str | None, Field(default=None, description="分區")]
    section_order: Annotated[int | None, Field(default=None, description="分區排序（數字越小越前面）")]
    description: Annotated[str | None, Field(default=None, description="餐點描述")]
    image: Annotated[str | None, Field(default=None, description="圖片")]
    created_at: Annotated[datetime, Field(description="建立時間")]
    updated_at: Annotated[datetime, Field(description="更新時間")]


class MenuReqModel(BaseModel):
    restaurant_id: uuid.UUID = Field(description="餐廳 ID")
    name: str = Field(description="餐點名稱")
    price: int = Field(ge=0, description="價格（新台幣，整數）")
    section: str | None = Field(default=None, description="分區（例：前菜／主餐／飲料），未填由系統歸為「未分類」")
    section_order: int | None = Field(default=None, ge=0, description="分區排序（數字越小越前面），未填預設 0")
    description: str | None = Field(default=None, description="餐點描述")
