import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class OrderItemRespModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[uuid.UUID, Field(description="訂單品項 ID")]
    menu_item_id: Annotated[uuid.UUID | None, Field(default=None, description="餐點 ID")]
    name: Annotated[str, Field(description="餐點名稱")]
    unit_price: Annotated[int, Field(description="單價（結帳當下快照）")]
    quantity: Annotated[int, Field(description="數量")]
    subtotal: Annotated[int, Field(description="小計")]


class OrderRespModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[uuid.UUID, Field(description="訂單 ID")]
    restaurant_id: Annotated[uuid.UUID | None, Field(default=None, description="餐廳 ID")]
    status: Annotated[str, Field(description="訂單狀態：pending/paid/failed/cancelled")]
    total_amount: Annotated[int, Field(description="訂單總金額")]
    merchant_trade_no: Annotated[str, Field(description="綠界特店交易編號")]
    ecpay_trade_no: Annotated[str | None, Field(default=None, description="綠界交易編號")]
    payment_date: Annotated[datetime | None, Field(default=None, description="付款時間")]
    items: Annotated[list[OrderItemRespModel], Field(description="訂單品項列表")]
    created_at: Annotated[datetime, Field(description="建立時間")]
    updated_at: Annotated[datetime, Field(description="更新時間")]


class CheckoutRespModel(BaseModel):
    order: Annotated[OrderRespModel, Field(description="新建立的訂單")]
    pay_url: Annotated[str, Field(description="前往付款的連結")]
