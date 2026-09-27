from unittest.mock import MagicMock

from database_errors.errors import Duplicate, Missing
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request

from src.exception_handle.handlers import (
    add_error_handler,
    authenticate_error_handler,
    database_error_handler,
    update_error_handler,
)


class TestExceptionHandlers:
    async def test_add_error_handler(self):
        response = await add_error_handler(MagicMock(spec=Request), Duplicate(msg="已存在"))

        assert response.status_code == 418
        assert response.body == b'{"code":418,"message":"\xe5\xb7\xb2\xe5\xad\x98\xe5\x9c\xa8"}'

    async def test_update_error_handler(self):
        response = await update_error_handler(MagicMock(spec=Request), Missing(msg="不存在"))

        assert response.status_code == 418

    async def test_authenticate_error_handler_keeps_401(self):
        """即使原始 HTTPException 帶入其他 status_code，也應統一轉成 401"""
        response = await authenticate_error_handler(
            MagicMock(spec=Request), HTTPException(status_code=403, detail="無權限")
        )

        assert response.status_code == 401

    async def test_database_error_handler(self):
        response = await database_error_handler(MagicMock(spec=Request), SQLAlchemyError("db error"))

        assert response.status_code == 500
