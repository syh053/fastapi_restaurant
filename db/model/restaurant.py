import uuid

from sqlalchemy import UUID, text, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from db.model.config import SCHEMA


class BaseModel(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=text("gen_random_uuid()"),
        primary_key=True,
        comment="ID"
    )


class DemoUser(BaseModel):
    __tablename__ = "demo_user"
    __table_args__ = SCHEMA

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="使用者名稱")
    age: Mapped[int] = mapped_column(Integer, nullable=False, comment="使用者年齡")
    sex: Mapped[str] = mapped_column(String(15), nullable=False, comment="使用者性別")
    remark: Mapped[str] = mapped_column(String(256), comment="備註欄")
