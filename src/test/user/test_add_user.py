from unittest.mock import AsyncMock

import bcrypt
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.user.add_user import AddUser
from src.vm.user.user_vm import UserAddReq


class TestAddUser:
    @pytest.fixture
    def mock_session(self) -> AsyncSession:
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncSession) -> AddUser:
        return AddUser(mock_session)

    @pytest.mark.parametrize(
        "user", [
            UserAddReq(
                name="Ben",
                email="ben@gmail.com",
                password="123",
                confirm_password="123",
            )
        ]
    )
    async def test_add_user(self, service: AddUser, user: UserAddReq) -> UserAddReq:
        result = await service.add_user(user)

        assert result == user

        return result

    @pytest.mark.parametrize(
        "user", [
            UserAddReq(
                name="",
                email="ben@gmail.com",
                password="123",
                confirm_password="123",
            ),
            UserAddReq(
                name="Ben",
                email="",
                password="123",
                confirm_password="123",
            ),
            UserAddReq(
                name="Ben",
                email="ben@gmail.com",
                password="",
                confirm_password="123",
            ),
            UserAddReq(
                name="Ben",
                email="ben@gmail.com",
                password="123",
                confirm_password="",
            ),
            UserAddReq(
                name="Ben",
                email="ben@gmail.com",
                password="123",
                confirm_password="321",
            )
        ]
    )
    async def test_add_user(self, service: AddUser, user: UserAddReq):
        with pytest.raises(HTTPException):
            await service.add_user(user)

    @pytest.mark.parametrize(
        "password", ["123"]
    )
    def test_get_hashed_password(self, password: str, service: AddUser):
        hashed = service._get_hashed_password(password)
        assert isinstance(hashed, str)
        assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
