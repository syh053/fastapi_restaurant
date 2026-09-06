import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class CartItemReqModel(BaseModel):
    menu_item_id: uuid.UUID = Field(description="餐點 ID")
    quantity: int = Field(default=1, ge=1, description="數量")


class CartItemUpdateReqModel(BaseModel):
    quantity: int = Field(ge=1, description="數量")


class CartItemRespModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[uuid.UUID, Field(description="購物車品項 ID")]
    menu_item_id: Annotated[uuid.UUID, Field(description="餐點 ID")]
    name: Annotated[str, Field(description="餐點名稱")]
    price: Annotated[int, Field(description="單價")]
    quantity: Annotated[int, Field(description="數量")]
    subtotal: Annotated[int, Field(description="小計")]
    image: Annotated[str | None, Field(default=None, description="餐點圖片")]
    restaurant_id: Annotated[uuid.UUID, Field(description="餐廳 ID")]
    restaurant_name: Annotated[str | None, Field(default=None, description="餐廳名稱")]
    created_at: Annotated[datetime, Field(description="加入時間")]
    updated_at: Annotated[datetime, Field(description="更新時間")]


class CartRespModel(BaseModel):
    items: Annotated[list[CartItemRespModel], Field(description="購物車品項列表")]
    total: Annotated[int, Field(description="總金額")]
