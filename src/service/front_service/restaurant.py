from typing import Sequence

from custom_select.select import select
from sqlalchemy import func

from sqlalchemy.ext.asyncio import AsyncSession


from db.model import Restaurant
from src.vm.end.restaurant_vm import EndRestaurantGetReqModel, EndRestaurantRespModel


class GetRestaurant:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all_restaurant(self, params: EndRestaurantGetReqModel) -> tuple[list[EndRestaurantRespModel], int]:
        stmt = (
            select(Restaurant, func.count(Restaurant.id).over().label("total"))
            .select_from(Restaurant)
            .where_if(params.name, lambda: Restaurant.name.ilike(f"%{params.name}%"))
            .where_if(params.tel, lambda: Restaurant.tel.ilike(f"%{params.tel}%"))
            .where_if(params.openingHours, lambda: Restaurant.openingHours.ilike(f"%{params.openingHours}%"))
            .where_if(params.address, lambda: Restaurant.address.ilike(f"%{params.address}%"))
            .where_if(params.description, lambda :Restaurant.description.ilike(f"%{params.description}%"))
            .offset((params.current_page - 1) * params.page_size)
            .limit(params.page_size)
        )
        results = await self._session.execute(stmt)

        results = results.fetchall()

        datas = [EndRestaurantRespModel.model_validate(result[0]) for result in results]
        total = results[0][1] if results else 0

        return datas, total