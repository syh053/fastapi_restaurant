from uuid import UUID

from database_errors.errors import Missing
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Comment
from src.service.basic.basic_service import BasicService


class CommentDeleteService(BasicService):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def delete_comment(self, restaurant_id: UUID, comment_id: UUID):
        """
        刪除餐廳評論並回傳成功刪除訊息

        :param restaurant_id: 餐廳 ID
        :param comment_id: 評論 ID
        :return: 回傳成功刪除評論訊息
        """
        # 檢查餐廳是否存在
        check_restaurant_existed = await self._check_if_existed_restaurant(self._session, restaurant_id)
        if not check_restaurant_existed:
            raise Missing(msg="餐廳不存在")

        # 檢查評論是否存在
        check_comment_existed = await self._check_if_existed_comment(self._session, comment_id)
        if not check_comment_existed:
            raise Missing(msg="評論不存在")

        if check_restaurant_existed and check_comment_existed:
            stmt = (
                delete(Comment).where(Comment.id == comment_id)
            )
            await self._session.execute(stmt)

        return {
            "code": 200,
            "message": "餐廳評論刪除成功!"
        }




