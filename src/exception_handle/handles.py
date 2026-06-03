from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse


async def unicorn_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=418,
        content={
            "code": exc.status_code,
            "message": exc.detail
        },
    )

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(
        HTTPException,
        unicorn_exception_handler
    )
