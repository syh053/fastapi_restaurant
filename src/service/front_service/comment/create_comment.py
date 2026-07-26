from database_errors.errors import Missing
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Comment
from src.dependencies.auth import get_current_user
from src.service.basic.basic_service import BasicService
from src.vm.comment.comment_vm import CommentCreateReqModel


class CommentService(BasicService):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_comment(self, session_id: str, comment: CommentCreateReqModel):
        """
        建立餐廳評論

        :param session_id: 從使用者 cookie 傳來的 session_id
        :param comment: comment 參數，詳見 comment_vm
        :return: 回傳建立餐廳評論成功訊息
        """
        # 檢查使用者是否存在
        user_info = await get_current_user(session_id)
        check_user_existed = await self._check_if_existed_user(self._session, user_info["user_id"])
        if not check_user_existed:
            raise Missing(msg="使用者不存在")

        # 檢查餐廳是否存在
        check_restaurant_existed = await self._check_if_existed_restaurant(self._session, comment.restaurant_id)
        if not check_restaurant_existed:
            raise Missing(msg="餐廳不存在")

        # 建立餐廳評論
        if check_user_existed and check_restaurant_existed:
            stmt = (
                insert(Comment).values({
                    "user_id": user_info["user_id"],
                    **comment.model_dump()
                })
            )
            await self._session.execute(stmt)

        return {
            "code": 200,
            "message": "餐聽評論建立成功!"
        }
