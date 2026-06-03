from custom_select.select import select
from errors import Duplicate
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Restaurant
from src.vm.end_restaurant.restaurant_vm import EndRestaurantAddReqModel


class CRUDRestaurant:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_restaurant(self, restaurant: EndRestaurantAddReqModel):
        existed = await self._check_if_existed_restaurant(restaurant.name)

        if not existed:
            stmt = insert(Restaurant).values(restaurant.model_dump())

            await self._session.execute(stmt)
            await self._session.commit()
        else:
            raise Duplicate(msg='此餐廳已存在')

    async def _check_if_existed_restaurant(self,name:str) -> bool:
        stmt = (
            select(Restaurant.name)
            .select_from(Restaurant)
            .where(Restaurant.name == name)
        )

        result = await self._session.execute(stmt)
        print("result :", result)

        if result:
            return True
        else:
            return False