from unittest import mock
from unittest.mock import AsyncMock

import bcrypt
import pytest
from fastapi import HTTPException

import uuid

from src.dependencies.auth import (
    check_password, get_current_user, require_admin, require_owner, require_admin_or_owner, get_owner_scope
)


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
        fake_session = {"user_id": "1", "user_name": "Ben", "role": "user"}

        with mock.patch("src.dependencies.auth.get_session", new=AsyncMock(return_value=fake_session)):
            result = await get_current_user(session_id="abc")

        assert result == fake_session


def _user(role) -> dict:
    return {"user_id": "11111111-1111-1111-1111-111111111111", "user_name": "Ben", "role": role}


class TestRequireAdmin:
    def test_require_admin_pass(self):
        user = _user("super_admin")
        assert require_admin(user=user) == user

    @pytest.mark.parametrize("role", ["user", "owner", False])
    def test_require_admin_forbidden(self, role):
        with pytest.raises(HTTPException) as exc_info:
            require_admin(user=_user(role))

        assert exc_info.value.status_code == 403

    def test_require_admin_legacy_bool_session(self):
        """舊 session 的 role=True 視為超級管理員"""
        user = _user(True)
        assert require_admin(user=user) == user


class TestRequireOwner:
    def test_require_owner_pass(self):
        user = _user("owner")
        assert require_owner(user=user) == user

    @pytest.mark.parametrize("role", ["user", "super_admin"])
    def test_require_owner_forbidden(self, role):
        with pytest.raises(HTTPException) as exc_info:
            require_owner(user=_user(role))

        assert exc_info.value.status_code == 403


class TestRequireAdminOrOwner:
    @pytest.mark.parametrize("role", ["owner", "super_admin"])
    def test_pass(self, role):
        user = _user(role)
        assert require_admin_or_owner(user=user) == user

    def test_forbidden_for_user(self):
        with pytest.raises(HTTPException) as exc_info:
            require_admin_or_owner(user=_user("user"))

        assert exc_info.value.status_code == 403


class TestGetOwnerScope:
    def test_owner_scoped_to_self(self):
        assert get_owner_scope(_user("owner")) == uuid.UUID("11111111-1111-1111-1111-111111111111")

    @pytest.mark.parametrize("role", ["super_admin", "user"])
    def test_others_not_scoped(self, role):
        assert get_owner_scope(_user(role)) is None
