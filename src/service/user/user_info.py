from uuid import UUID

from custom_select.select import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import User, Comment, Restaurant
from src.vm.user.user_info_vm import UserInfoRespModel


class GetUserInfoService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_info(self, user_id: UUID):
        """
        取得使用者資訊、餐廳評論資料，以及評論總數

        :param user_id: 使用者 ID
        :return: 回傳使用者資訊以及歷史餐廳評論
        """
        restaurant_count = (
            select(func.count(func.distinct(Comment.restaurant_id)))
            .where(Comment.user_id == user_id)
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
            .where(User.id == user_id)
            .distinct(Restaurant.id)
        )
        results = await self._session.execute(stmt)
        results = results.all()

        # 從第一筆結果取得 User 物件
        user = results[0][0]

        # 取得 restaurants
        restaurants = [
            restaurant
            for _, restaurant, _ in results
            if restaurant is not None
        ]

        return UserInfoRespModel(
            id=user.id,
            name=user.name,
            email=user.email,
            image=user.image,
            is_admin=user.is_admin,
            restaurants=[restaurant for restaurant in restaurants],
            comments_total=results[0][2]
        )
