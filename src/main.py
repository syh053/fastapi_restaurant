import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

import uvicorn

from src.router import TOTAL_ROUTER

WEB_SERVER_SETTING = {
    "app": "main:app",
    "host": "127.0.0.1",
    "port": 8888,
    "reload": True,
    "reload_excludes": [".venv"],
}

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(f"互動式 API 文件 : http://127.0.0.1:{WEB_SERVER_SETTING['port']}/docs")
    yield
    logger.info("伺服器已關閉!")

app = FastAPI(lifespan=lifespan)
app.include_router(TOTAL_ROUTER)

if __name__ == "__main__":
    uvicorn.run(**WEB_SERVER_SETTING)