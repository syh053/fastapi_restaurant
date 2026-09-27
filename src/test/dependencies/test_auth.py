from unittest import mock
from unittest.mock import AsyncMock

import bcrypt
import pytest
from fastapi import HTTPException

from src.dependencies.auth import check_password, get_current_user, require_admin


class TestCheckPassword:
    def test_check_password_correct(self):
        hashed = bcrypt.hashpw("123".encode("utf-8"), salt=bcrypt.gensalt())
        assert check_password("123".encode("utf-8"), hashed) is True

    def test_check_password_incorrect(self):
        hashed = bcrypt.hashpw("123".encode("utf-8"), salt=bcrypt.gensalt())
        assert check_password("wrong".encode("utf-8"), hashed) is False


class TestGetCurrentUser:
    async def test_no_session_id(self):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(session_id=None)

        assert exc_info.value.status_code == 401

    async def test_session_not_found_or_expired(self):
        with mock.patch("src.dependencies.auth.get_session", new=AsyncMock(return_value=None)):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(session_id="abc")

        assert exc_info.value.status_code == 401

    async def test_valid_session(self):
        fake_session = {"user_id": "1", "user_name": "Ben", "role": False}

        with mock.patch("src.dependencies.auth.get_session", new=AsyncMock(return_value=fake_session)):
            result = await get_current_user(session_id="abc")

        assert result == fake_session


class TestRequireAdmin:
    def test_require_admin_pass(self):
        user = {"user_id": "1", "user_name": "Ben", "role": True}
        assert require_admin(user=user) == user

    def test_require_admin_forbidden(self):
        user = {"user_id": "1", "user_name": "Ben", "role": False}
        with pytest.raises(HTTPException) as exc_info:
            require_admin(user=user)

        assert exc_info.value.status_code == 403
