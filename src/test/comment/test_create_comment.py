from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.comment.create_comment import CommentCreateService
from src.vm.comment.comment_vm import CommentCreateReqModel

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")


class TestCommentCreateService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> CommentCreateService:
        return CommentCreateService(mock_session)

    @pytest.fixture
    def comment(self) -> CommentCreateReqModel:
        return CommentCreateReqModel(text="好吃!", restaurant_id=RESTAURANT_ID)

    async def test_create_comment(self, service: CommentCreateService, comment: CommentCreateReqModel):
        service._check_if_existed_restaurant = AsyncMock(return_value=True)

        result = await service.create_comment(user_id=USER_ID, comment=comment)

        service._check_if_existed_restaurant.assert_awaited_once_with(service._session, RESTAURANT_ID)
        service._session.execute.assert_awaited_once()  # type: ignore
        stmt = str(service._session.execute.call_args[0][0])  # type: ignore
        assert "INSERT INTO restaurant.comment" in stmt
        assert result["code"] == 200

    async def test_create_comment_restaurant_missing(
            self, service: CommentCreateService, comment: CommentCreateReqModel
    ):
        service._check_if_existed_restaurant = AsyncMock(return_value=False)

        with pytest.raises(Missing):
            await service.create_comment(user_id=USER_ID, comment=comment)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_create_comment_with_different_restaurant(self, service: CommentCreateService):
        other_comment = CommentCreateReqModel(text="還可以", restaurant_id=uuid4())
        service._check_if_existed_restaurant = AsyncMock(return_value=True)

        await service.create_comment(user_id=USER_ID, comment=other_comment)

        service._check_if_existed_restaurant.assert_awaited_once_with(service._session, other_comment.restaurant_id)
