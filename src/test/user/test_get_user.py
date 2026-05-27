from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.user.get_user import GetUser
from src.vm.user.user_vm import UserGetReqModel, UserGetRespModel


class TestGetUser:
    @pytest.fixture
    def mock_session(self) -> AsyncSession:
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncSession) -> GetUser:
        return GetUser(mock_session)

    @pytest.fixture
    def response(self) -> MagicMock:
        return MagicMock(spec=Response)

    @pytest.mark.parametrize(
        "user", [
            UserGetReqModel(
                name="Ben",
                password="123",
            )
        ]
    )
    async def test_login(self, service: GetUser, user: UserGetReqModel, response: MagicMock):
        """
        登入測試，將 login 中的外部函式 check_password 及 create_access_token 替換成 mock，內部方法
        _get_user_from_db 也替換為 AsyncMock()，來模擬成功的登入

        :param service: 由 pytest.fixture 提供，session 替換為 AsyncMock()
        :param user: 由 pytest.mark.parametrize 傳入的假資料
        :param response: 替換為 AsyncMock(spec=Response)
        :return: 無回傳值
        """
        fake_db_user = UserGetRespModel(name="Ben", email="ben@gmail.com", password="123", is_admin=False)
        service._get_user_from_db = AsyncMock(return_value=fake_db_user)

        with (
            mock.patch("src.service.user.get_user.check_password", return_value=True),
            mock.patch("src.service.user.get_user.create_access_token", return_value="fake_token") as mock_token,
        ):
            await service.login(user, response)

        mock_token.assert_called_once_with(user_id="Ben", is_admin=False)
        response.set_cookie.assert_called_once_with(
            key="access_token",
            value="fake_token",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24
        )
