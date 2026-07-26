from typing import TypeVar
from uuid import UUID

from custom_select.select import select
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Comment, User, Restaurant
from src.vm.comment.comment_vm import CommentGetRespModel

T = TypeVar("T", bound=BaseModel)

class CommentGetService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_restaurant_comment(self, restaurant_id: UUID) -> list[CommentGetRespModel]:
        """
        回傳餐廳列表

        :param restaurant_id: 餐廳 ID
        :return: 回傳餐廳列表
        """
        stmt = (
            select(
                Restaurant.name.label("restaurant_name"),
                User.name.label("user_name"),
                Comment.id.label("comment_id"),
                Comment.text.label("comment"),
                Comment.created_at,
                Comment.updated_at,
            )
            .join(Comment, Comment.restaurant_id == Restaurant.id)
            .join(User, User.id == Comment.user_id)
            .where(Restaurant.id == restaurant_id)
            .order_by(Comment.created_at.desc())
        )
        results = await self._session.execute(stmt)

        results = results.all()

        datas = self._rows_to_models(results, CommentGetRespModel)

        return datas

    @staticmethod
    def _rows_to_models(results, as_class: type[T]) -> list[T]:
        """
        將 SQLAlchemy Query 結果轉換為指定的 Pydantic Model

        :param results: SQLAlchemy 查詢結果
        :param as_class: 要轉換成的 Pydantic Model 類別
        :return: 指定的 Pydantic Model 組成的列表
        """
        return [
            as_class.model_validate(result)

            for result in results
        ]
