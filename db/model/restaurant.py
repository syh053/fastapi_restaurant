from model_basic import BaseModel
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import mapped_column, Mapped

from db.model.config import SCHEMA


class Restaurant(BaseModel):
    __tablename__ = "restaurant"
    __table_args__ = SCHEMA

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="餐廳名稱")
    tel: Mapped[str] = mapped_column(String(128), nullable=False, comment="餐廳電話")
    openingHours: Mapped[int] = mapped_column(Integer, nullable=False, comment="營業時長")
    address: Mapped[str] = mapped_column(String(256), nullable=False, comment="餐廳地址")
    description: Mapped[str] = mapped_column(Text, nullable=True, comment="備註")
