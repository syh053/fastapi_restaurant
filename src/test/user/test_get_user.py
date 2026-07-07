from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
from errors import Missing
from fastapi import Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.user.get_user import GetUser
from src.vm.user.user_vm import UserGetReqModel, UserGetRespModel


class TestGetUser:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
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

    @pytest.fixture
    def user(self) -> UserGetReqModel:
        return UserGetReqModel(name="Ben", password="123")

    async def test_login(self, service: GetUser, user: UserGetReqModel, response: MagicMock):
        """
        登入測試，將 get_user.py 中的外部函式 check_password 及 create_access_token 替換成 mock，
        內部方法 _get_user_from_db 也替換為 AsyncMock()，來模擬成功的登入

        :param service: 由 pytest.fixture 提供，session 替換為 AsyncMock()
        :param user: 由 pytest.fixture 提供的假資料
        :param response: 替換為 AsyncMock(spec=Response)
        :return: 無回傳值
        """
        fake_db_user = UserGetRespModel(name="Ben", email="ben@gmail.com", password="123", is_admin=False)
        service._get_user_from_db = AsyncMock(return_value=fake_db_user)

        with (
            mock.patch("src.service.user.get_user.check_password", return_value=True),
            mock.patch("src.service.user.get_user.create_session", new_callable=AsyncMock) as mock_session,
        ):
            await service.login(user, response)

        # 驗證 _get_user_from_db 是否有被呼叫
        service._get_user_from_db.assert_awaited_once_with(
            "Ben",
            as_class=UserGetRespModel
        )

        # 驗證 create_session
        mock_session.assert_called_once()

        session_id, data = mock_session.call_args.args
        expires = mock_session.call_args.kwargs["expires"]

        assert isinstance(session_id, str)
        assert data == {
            "user_id": "Ben",
            "role": False
        }
        assert expires == 60 * 60 * 6

        # 驗證 cookie
        response.set_cookie.assert_called_once_with(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            # samesite="lax",
            max_age=60 * 60 * 24
        )

    async def test_login_with_error(self, service: GetUser, user: UserGetReqModel, response: MagicMock):
        """
        將 get_user.py 中的外部函式 check_password 替換成 AsyncMock
        內部方法 _get_user_from_db 也替換為 AsyncMock()，，模擬輸入錯誤的密碼

        :param service: 由 pytest.fixture 提供，session 替換為 AsyncMock()
        :param user: 由 pytest.fixture 提供的假資料
        :param response: 替換為 AsyncMock(spec=Response)
        :return: 無回傳值
        """
        fake_db_user = UserGetRespModel(name="Ben", email="ben@gmail.com", password="123", is_admin=False)
        service._get_user_from_db = AsyncMock(return_value=fake_db_user)

        with (
            mock.patch("src.service.user.get_user.check_password", return_value=False),
        ):
            with pytest.raises(HTTPException):
                await service.login(user, response)

    async def test_login_with_missing(self, service: GetUser, user: UserGetReqModel, response: MagicMock):
        """
        將 GetUser 中的內部函式 _get_user_from_db 替換成 AsyncMock，模擬輸入錯誤的密碼

        :param service: 由 pytest.fixture 提供，session 替換為 AsyncMock()
        :param user: 由 pytest.fixture 提供的假資料
        :param response: 替換為 AsyncMock(spec=Response)
        :return:
        """
        service._get_user_from_db = AsyncMock(side_effect=Missing(msg="無此名稱!"))

        with pytest.raises(Missing):
            await service.login(user, response)
