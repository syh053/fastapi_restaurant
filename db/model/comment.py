from datetime import datetime
import uuid


from model_basic.model_basic import BaseModel
from sqlalchemy import Text, UUID, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from db.model.config import SCHEMA


class Comment(BaseModel):
    __tablename__ = "comment"
    __table_args__ = SCHEMA

    text: Mapped[str] = mapped_column(Text, nullable=False, comment="餐廳評論")
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.restaurant.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=False,
        comment="餐廳 ID"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("restaurant.user.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=False,
        comment="使用者 ID"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(
        timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="建立時間"
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(
        timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="修改時間"
    )
