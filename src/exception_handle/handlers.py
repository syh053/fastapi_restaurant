import logging

from database_errors.errors import Duplicate, Missing
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

async def add_error_handler(_request: Request, exc: Duplicate):
    return JSONResponse(
        status_code=418,
        content={
            "code": 418,
            "message": exc.msg
        },
    )

async def update_error_handler(_request: Request, exc: Missing):
    return JSONResponse(
        status_code=418,
        content={
            "code": 418,
            "message": exc.msg
        },
    )

async def authenticate_error_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=401,
        content={
            "code": 401,
            "message": exc.detail
        }
    )

async def database_error_handler(_request: Request, exc: SQLAlchemyError):
    logger.exception("資料庫操作發生未預期例外", exc_info=exc)

    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "資料庫操作發生錯誤，請稍後再試"
        },
    )