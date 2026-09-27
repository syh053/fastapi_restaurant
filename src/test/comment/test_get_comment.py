from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.comment.get_comment import CommentGetService
from src.vm.comment.comment_vm import CommentGetRespModel

RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")


def _row(**overrides) -> SimpleNamespace:
    data = dict(
        restaurant_name="玉堂春魯肉飯",
        user_name="Ben",
        comment_id=UUID("33333333-3333-3333-3333-333333333333"),
        comment="好吃!",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    data.update(overrides)
    return SimpleNamespace(**data)


class TestCommentGetService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> CommentGetService:
        return CommentGetService(mock_session)

    async def test_get_restaurant_comment(self, service: CommentGetService, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.all.return_value = [_row()]
        mock_session.execute.return_value = execute_result

        results = await service.get_restaurant_comment(RESTAURANT_ID)

        mock_session.execute.assert_awaited_once()
        assert isinstance(results, list)
        assert isinstance(results[0], CommentGetRespModel)
        assert results[0].comment == "好吃!"

    async def test_get_restaurant_comment_user_deleted(self, service: CommentGetService, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.all.return_value = [_row(user_name="使用者已刪除")]
        mock_session.execute.return_value = execute_result

        results = await service.get_restaurant_comment(RESTAURANT_ID)

        assert results[0].user_name == "使用者已刪除"

    async def test_get_restaurant_comment_empty(self, service: CommentGetService, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.all.return_value = []
        mock_session.execute.return_value = execute_result

        results = await service.get_restaurant_comment(RESTAURANT_ID)

        assert results == []
