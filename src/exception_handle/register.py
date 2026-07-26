from database_errors.errors import Duplicate, Missing
from fastapi import FastAPI, HTTPException

from src.exception_handle.handlers import update_error_handler, add_error_handler, authenticate_error_handler


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(
        Duplicate,
        add_error_handler
    )

    app.add_exception_handler(
        Missing,
        update_error_handler
    )

    app.add_exception_handler(
        HTTPException,
        authenticate_error_handler
    )
