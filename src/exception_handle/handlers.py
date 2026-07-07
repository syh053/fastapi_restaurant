from errors import Missing, Duplicate
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