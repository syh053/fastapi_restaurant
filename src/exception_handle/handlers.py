from database_errors.errors import Duplicate, Missing
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

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