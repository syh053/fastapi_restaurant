import os
from pathlib import Path

import uvicorn
from core.fastapi_app import FastAPIApp
from starlette.staticfiles import StaticFiles

from src.exception_handle.register import register_exception_handlers
from src.router import TOTAL_ROUTER

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "uploads"

WEB_SERVER_SETTING = {
    "app": "main:app",
    "host": "127.0.0.1",
    "port": int(os.environ.get("PORT", 8888)),
    "reload": True,
    "reload_excludes": [".venv"],
}

# 定義允許跨域請求的來源名單
ALLOW_ORIGINS = [
    "http://localhost:5173",
    "https://vue-restaurnat.onrender.com",
    "https://vue-restaurant.zeabur.app",
    "https://bebetterryan.com",
]

app = (
    FastAPIApp(
        port=WEB_SERVER_SETTING["port"],
        router=TOTAL_ROUTER,
        allow_origins=ALLOW_ORIGINS,
    )
    .get_app()
)

register_exception_handlers(app=app)

app.mount("/assets", StaticFiles(directory=UPLOAD_DIR), name="static")

if __name__ == "__main__":
    uvicorn.run(**WEB_SERVER_SETTING)
