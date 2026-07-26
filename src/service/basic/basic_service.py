from uuid import UUID

from custom_select.select import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import User, Restaurant, Comment


class BasicService:
    @staticmethod
    async def _check_if_existed_user(session: AsyncSession, user_id: UUID) -> bool:
        """
        從資料庫取得使用者資訊

        :param session: 執行資料庫查詢的 session
        :param user_id: 使用者 ID
        :return: 確認使用者是否存在
        """
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)

        return result.scalar_one_or_none() is not None

    @staticmethod
    async def _check_if_existed_restaurant(session: AsyncSession, restaurant_id: UUID) -> bool:
        """

        :param session: 執行資料庫查詢的 session
        :param restaurant_id: 餐廳 ID
        :return: 確認餐廳是否存在
        """
        stmt = (
            select(Restaurant.name)
            .where(Restaurant.id == restaurant_id)
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none() is not None

    @staticmethod
    async def _check_if_existed_comment(session: AsyncSession, comment_id: UUID):
        """

        :param session: 執行資料庫查詢的 session
        :param comment_id: 評論 ID
        :return: 確認評論是否存在
        """
        stmt = (
            select(Comment)
            .where(Comment.id == comment_id)
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none() is not None
