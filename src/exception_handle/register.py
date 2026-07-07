from errors import Missing, Duplicate
from fastapi import FastAPI

from src.exception_handle.handlers import update_error_handler, add_error_handler


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(
        Duplicate,
        add_error_handler
    )

    app.add_exception_handler(
        Missing,
        update_error_handler
    )
