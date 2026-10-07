from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.end_service.user import UserCrud
from src.vm.end.user_vm import EndUserGetReqModel, EndUserRespModel, EndUserUpdateReqModel

USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def _user(**overrides) -> SimpleNamespace:
    data = dict(id=USER_ID, name="Ben", email="ben@gmail.com", role="user")
    data.update(overrides)
    return SimpleNamespace(**data)


class TestUserCrud:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.scalar = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> UserCrud:
        return UserCrud(mock_session)

    # --- get_users ---

    async def test_get_users(self, service: UserCrud, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.all.return_value = [(_user(), 1)]
        mock_session.execute.return_value = execute_result

        params = EndUserGetReqModel(current_page=1, page_size=10)
        datas, total = await service.get_users(params)

        mock_session.execute.assert_awaited_once()
        assert isinstance(datas[0], EndUserRespModel)
        assert total == 1

    async def test_get_users_empty(self, service: UserCrud, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.all.return_value = []
        mock_session.execute.return_value = execute_result

        params = EndUserGetReqModel(current_page=1, page_size=10)
        datas, total = await service.get_users(params)

        assert datas == []
        assert total == 0

    async def test_get_users_with_filters(self, service: UserCrud, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.all.return_value = [(_user(), 1)]
        mock_session.execute.return_value = execute_result

        params = EndUserGetReqModel(name="Ben", email="ben", role="user", current_page=1, page_size=10)
        await service.get_users(params)

        mock_session.execute.assert_awaited_once()

    # --- update_user_access ---

    async def test_update_user_access(self, service: UserCrud):
        service._check_if_existed_user = AsyncMock(return_value=True)
        params = EndUserUpdateReqModel(id=USER_ID, role="owner")

        await service.update_user_access(params)

        service._check_if_existed_user.assert_awaited_once_with(USER_ID)
        service._session.execute.assert_awaited_once()  # type: ignore

    async def test_update_user_access_missing(self, service: UserCrud):
        service._check_if_existed_user = AsyncMock(return_value=False)
        params = EndUserUpdateReqModel(id=USER_ID, role="owner")

        with pytest.raises(Missing):
            await service.update_user_access(params)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_update_user_access_cannot_demote_self(self, service: UserCrud):
        params = EndUserUpdateReqModel(id=USER_ID, role="user")

        with pytest.raises(HTTPException) as exc_info:
            await service.update_user_access(params, current_user_id=USER_ID)

        assert exc_info.value.status_code == 400
        service._session.execute.assert_not_awaited()  # type: ignore

    # --- delete_user ---

    async def test_delete_user(self, service: UserCrud):
        service._check_if_existed_user = AsyncMock(side_effect=[True, True])

        await service.delete_user([USER_ID, uuid4()])

        service._session.execute.assert_awaited_once()  # type: ignore
        stmt = str(service._session.execute.call_args[0][0])  # type: ignore
        assert 'DELETE FROM restaurant."user"' in stmt

    async def test_delete_user_missing(self, service: UserCrud):
        service._check_if_existed_user = AsyncMock(side_effect=[True, False])

        with pytest.raises(Missing):
            await service.delete_user([USER_ID, uuid4()])

        service._session.execute.assert_not_awaited()  # type: ignore

    # --- _check_if_existed_user ---

    async def test_check_if_existed_user_true(self, service: UserCrud, mock_session: AsyncMock):
        mock_session.scalar.return_value = _user()

        assert await service._check_if_existed_user(USER_ID) is True

    async def test_check_if_existed_user_false(self, service: UserCrud, mock_session: AsyncMock):
        mock_session.scalar.return_value = None

        assert await service._check_if_existed_user(USER_ID) is False
