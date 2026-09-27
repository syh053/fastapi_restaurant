from unittest.mock import MagicMock

from database_errors.errors import Duplicate, Missing
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from src.exception_handle.register import register_exception_handlers


class TestRegisterExceptionHandlers:
    def test_registers_all_handlers(self):
        app = MagicMock(spec=FastAPI)

        register_exception_handlers(app)

        registered_exceptions = [call.args[0] for call in app.add_exception_handler.call_args_list]
        assert registered_exceptions == [Duplicate, Missing, HTTPException, SQLAlchemyError]
        assert app.add_exception_handler.call_count == 4
