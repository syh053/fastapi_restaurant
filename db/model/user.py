from model_basic.model_basic import BaseModel
from sqlalchemy import String, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column

from db.model.config import SCHEMA


class User(BaseModel):
    __tablename__ = "user"
    __table_args__ = SCHEMA

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="使用者名稱")
    email: Mapped[str] = mapped_column(String(256), nullable=False, comment="email")
    password: Mapped[str] = mapped_column(String(128), nullable=False, comment="使用者密碼")
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False, comment="是否為管理員")

