import sys
from pathlib import Path
from typing import AsyncGenerator

from configuration.configuration import Configuration
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

top_dir = Path(sys.prefix).resolve().parent

sys.path.append(str(top_dir))
db_config = Configuration(top_dir / "sys.ini")

async_engine = create_async_engine(db_config["DATABASE"]["sqlalchemy.url"],
                                   echo=db_config.getboolean("DATABASE", "echo")
                                   )
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # 若沒有 Exception，就自動提交
        except Exception:
            await session.rollback()  # 若發生異常，立刻回滾
            raise  # 將錯誤繼續往外丟，讓 FastAPI 的 Exception Handler 處理
