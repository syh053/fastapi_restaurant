import uuid
from datetime import datetime

from model_basic.model_basic import BaseModel
from sqlalchemy import String, Integer, UUID, ForeignKey, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column

from db.model.config import SCHEMA


class Order(BaseModel):
    __tablename__ = "order"
    __table_args__ = SCHEMA

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="使用者 ID"
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.restaurant.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="餐廳 ID"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        server_default=text("'pending'"),
        nullable=False,
        comment="訂單狀態：pending/paid/failed/cancelled"
    )
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="訂單總金額（新台幣，整數）")
    merchant_trade_no: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        comment="綠界特店交易編號（MerchantTradeNo）"
    )
    ecpay_trade_no: Mapped[str] = mapped_column(
        String(30), nullable=True, comment="綠界交易編號（TradeNo）"
    )
    payment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="綠界回傳的付款時間"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="建立時間"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新時間"
    )


class OrderItem(BaseModel):
    __tablename__ = "order_item"
    __table_args__ = SCHEMA

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.order.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="訂單 ID"
    )
    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.menu_item.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="餐點 ID"
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="餐點名稱（結帳當下快照）")
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False, comment="單價（結帳當下快照）")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, comment="數量")
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False, comment="小計")
