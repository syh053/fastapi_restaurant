from custom_select.select import select
from errors import Duplicate, Missing
from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Restaurant
from src.vm.end_restaurant.restaurant_vm import EndRestaurantReqModel


class CRUDRestaurant:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_restaurant(self, restaurant: EndRestaurantReqModel) -> None:
        """
        新增餐廳功能

        :param restaurant: 新增的餐廳資訊
        :return: 無
        """
        existed = await self._check_if_existed_restaurant(restaurant.name)

        if not existed:
            stmt = insert(Restaurant).values(restaurant.model_dump())

            await self._session.execute(stmt)
            await self._session.commit()
        else:
            raise Duplicate(msg='此餐廳已存在')

    async def update_restaurant(self, original_name: str, restaurant: EndRestaurantReqModel) -> None:
        """

        :param original_name: 原來的餐廳名稱
        :param restaurant: 欲修改的餐廳內容
        :return: 無
        """
        existed = await self._check_if_existed_restaurant(original_name)

        if existed:
            stmt = update(Restaurant).values(restaurant.model_dump()).where(Restaurant.name == original_name)

            await self._session.execute(stmt)
            await self._session.commit()
        else:
            raise Missing(msg="餐廳不存在")

    async def delete_restaurant(self, restaurant_name_list: list[str]) -> None:
        """

        :param restaurant_name_list: 欲刪除的餐廳名稱
        :type restaurant_name_list: list[str]
        :return: 無
        """
        for name in restaurant_name_list:
            existed = await self._check_if_existed_restaurant(name)
            if not existed:
                raise Missing(msg=f"餐廳 {name} 不存在，取消所有刪除，請確認。")

        stmt = delete(Restaurant).where(Restaurant.name.in_(restaurant_name_list))

        await self._session.execute(stmt)
        await self._session.commit()

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
