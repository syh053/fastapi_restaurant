from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.comment.delete_comment import CommentDeleteService

RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")
COMMENT_ID = UUID("33333333-3333-3333-3333-333333333333")


class TestCommentDeleteService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> CommentDeleteService:
        return CommentDeleteService(mock_session)

    async def test_delete_comment(self, service: CommentDeleteService):
        service._check_if_existed_restaurant = AsyncMock(return_value=True)
        service._check_if_existed_comment = AsyncMock(return_value=True)

        result = await service.delete_comment(restaurant_id=RESTAURANT_ID, comment_id=COMMENT_ID)

        service._check_if_existed_restaurant.assert_awaited_once_with(service._session, RESTAURANT_ID)
        service._check_if_existed_comment.assert_awaited_once_with(service._session, COMMENT_ID)
        service._session.execute.assert_awaited_once()  # type: ignore
        stmt = str(service._session.execute.call_args[0][0])  # type: ignore
        assert "DELETE FROM restaurant.comment" in stmt
        assert result["code"] == 200

    async def test_delete_comment_restaurant_missing(self, service: CommentDeleteService):
        service._check_if_existed_restaurant = AsyncMock(return_value=False)
        service._check_if_existed_comment = AsyncMock(return_value=True)

        with pytest.raises(Missing):
            await service.delete_comment(restaurant_id=RESTAURANT_ID, comment_id=COMMENT_ID)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_delete_comment_comment_missing(self, service: CommentDeleteService):
        service._check_if_existed_restaurant = AsyncMock(return_value=True)
        service._check_if_existed_comment = AsyncMock(return_value=False)

        with pytest.raises(Missing):
            await service.delete_comment(restaurant_id=RESTAURANT_ID, comment_id=COMMENT_ID)

        service._session.execute.assert_not_awaited()  # type: ignore
