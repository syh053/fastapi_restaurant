from custom_select.select import select
from errors import Duplicate, Missing
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Restaurant
from src.vm.end_restaurant.restaurant_vm import EndRestaurantReqModel


class CRUDRestaurant:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_restaurant(self, restaurant: EndRestaurantReqModel):
        existed = await self._check_if_existed_restaurant(restaurant.name)

        if not existed:
            stmt = insert(Restaurant).values(restaurant.model_dump())

            await self._session.execute(stmt)
            await self._session.commit()
        else:
            raise Duplicate(msg='此餐廳已存在')

    async def update_restaurant(self, original_name: str, restaurant: EndRestaurantReqModel):
        existed = await self._check_if_existed_restaurant(original_name)

        if existed:
            stmt = update(Restaurant).values(restaurant.model_dump()).where(Restaurant.name == original_name)

            await self._session.execute(stmt)
            await self._session.commit()
        else:
            raise Missing(msg="餐廳不存在")

    async def _check_if_existed_restaurant(self, name: str) -> bool:
        stmt = (
            select(Restaurant.name)
            .select_from(Restaurant)
            .where(Restaurant.name == name)
        )

        result = await self._session.execute(stmt)

        if result.scalar_one_or_none():
            return True
        else:
            return False
