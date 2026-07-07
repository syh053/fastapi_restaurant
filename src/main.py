import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.exception_handle.register import register_exception_handlers
from src.router import TOTAL_ROUTER

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "uploads"

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
app.mount("/assets", StaticFiles(directory=UPLOAD_DIR), name="static")

register_exception_handlers(app=app)

# 設定跨來源請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(**WEB_SERVER_SETTING)
