from uuid import UUID

from custom_select.select import select
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import User, Comment, Restaurant
from src.dependencies.auth import get_current_user
from src.vm.user.user_info_vm import UserInfoReqModel


class GetUserInfo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_info(self, session_id: str):
        """
        取得使用者資訊、餐廳評論資料，以及評論總數

        :param session_id: 登入者  session_id
        :return: 回傳使用者資訊以及歷史餐廳評論
        """
        # 取得目前使用者 ID
        user_info = await get_current_user(session_id)
        current_user_id = user_info["user_id"]

        restaurant_count = (
            select(func.count(func.distinct(Comment.restaurant_id)))
            .where(Comment.user_id == current_user_id)
            .scalar_subquery()
        )

        stmt = (
            select(
                User,
                Restaurant,
                restaurant_count.label("restaurants_total"),
            )
            .outerjoin(Comment, Comment.user_id == User.id)
            .outerjoin(Restaurant, Restaurant.id == Comment.restaurant_id)
            .where(User.id == current_user_id)
            .distinct(Restaurant.id)
        )
        results = await self._session.execute(stmt)
        results = results.all()

        print('目前只用者 ID :', current_user_id)
        print('results :', results)
        print(results[0][0].__dict__)

        # 從第一筆結果取得 User 物件
        user = results[0][0]

        # 取得 restaurants
        restaurants = [
            restaurant
            for _, restaurant, _ in results
            if restaurant is not None
        ]

        return UserInfoReqModel(
            id=user.id,
            name=user.name,
            email=user.email,
            is_admin=user.is_admin,
            # comments=[comment for comment in comments],
            restaurants=[restaurant for restaurant in restaurants],
            # comments_total=results[0][3]
            comments_total=results[0][2]
        )
