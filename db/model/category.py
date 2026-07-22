from model_basic.model_basic import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.model.config import SCHEMA


class  Category(BaseModel):
    __tablename__ = "category"
    __table_args__ = SCHEMA

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="分類名稱")

