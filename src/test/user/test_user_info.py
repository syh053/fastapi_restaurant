from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.user.user_info import GetUserInfoService
from src.vm.user.user_info_vm import UserInfoRespModel

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")
OTHER_RESTAURANT_ID = UUID("33333333-3333-3333-3333-333333333333")


def _user(**overrides) -> SimpleNamespace:
    data = dict(id=USER_ID, name="Ben", email="ben@gmail.com", image=None, is_admin=False)
    data.update(overrides)
    return SimpleNamespace(**data)


def _restaurant(**overrides) -> SimpleNamespace:
    data = dict(
        id=RESTAURANT_ID,
        name="玉堂春魯肉飯",
        tel="04-23013008",
        openingHours=6,
        address="臺中市西區中興里美村路一段220號",
        description=None,
        image=None,
        category_id=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    data.update(overrides)
    return SimpleNamespace(**data)


class TestGetUserInfoService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> GetUserInfoService:
        return GetUserInfoService(mock_session)

    async def test_get_user_info_with_restaurants(self, service: GetUserInfoService, mock_session: AsyncMock):
        user = _user()
        execute_result = MagicMock()
        execute_result.all.return_value = [
            (user, _restaurant(), 2),
            (user, _restaurant(id=OTHER_RESTAURANT_ID), 2),
        ]
        mock_session.execute.return_value = execute_result

        result = await service.get_user_info(USER_ID)

        mock_session.execute.assert_awaited_once()
        assert isinstance(result, UserInfoRespModel)
        assert result.id == USER_ID
        assert result.comments_total == 2
        assert len(result.restaurants) == 2

    async def test_get_user_info_without_comments(self, service: GetUserInfoService, mock_session: AsyncMock):
        user = _user()
        execute_result = MagicMock()
        execute_result.all.return_value = [(user, None, 0)]
        mock_session.execute.return_value = execute_result

        result = await service.get_user_info(USER_ID)

        assert result.restaurants == []
        assert result.comments_total == 0
