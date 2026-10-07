from model_basic.model_basic import BaseModel
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from db.model.config import SCHEMA
from db.model.enums import UserRole


class User(BaseModel):
    __tablename__ = "user"
    __table_args__ = SCHEMA

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="使用者名稱")
    email: Mapped[str] = mapped_column(String(256), nullable=False, comment="email")
    password: Mapped[str] = mapped_column(String(128), nullable=False, comment="使用者密碼")
    role: Mapped[str] = mapped_column(
        String(20),
        server_default=text(f"'{UserRole.USER}'"),
        nullable=False,
        comment="角色:user / owner / super_admin"
    )
    image: Mapped[str] = mapped_column(String(256), nullable=True, comment="圖片連結")
