import uuid
from datetime import datetime

from model_basic.model_basic import BaseModel
from sqlalchemy import String, Text, Integer, UUID, ForeignKey, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column

from db.model.config import SCHEMA


class MenuItem(BaseModel):
    __tablename__ = "menu_item"
    __table_args__ = SCHEMA

    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.restaurant.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="餐廳 ID"
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="餐點名稱")
    price: Mapped[int] = mapped_column(Integer, nullable=False, comment="價格（新台幣，整數）")
    section: Mapped[str] = mapped_column(
        String(64),
        server_default=text("'未分類'"),
        nullable=False,
        comment="分區（例：前菜／主餐／飲料）"
    )
    section_order: Mapped[int] = mapped_column(
        Integer,
        server_default=text("0"),
        nullable=False,
        comment="分區排序（數字越小越前面，預設 0）"
    )
    description: Mapped[str] = mapped_column(Text, nullable=True, comment="餐點描述")
    image: Mapped[str] = mapped_column(String(256), nullable=True, comment="圖片連結")
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
