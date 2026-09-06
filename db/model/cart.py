import uuid
from datetime import datetime

from model_basic.model_basic import BaseModel
from sqlalchemy import Integer, UUID, ForeignKey, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column

from db.model.config import SCHEMA


class Cart(BaseModel):
    __tablename__ = "cart"
    __table_args__ = SCHEMA

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="使用者 ID"
    )
    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.menu_item.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="餐點 ID"
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        server_default=text("1"),
        nullable=False,
        comment="數量"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="建立時間"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新時間"
    )
