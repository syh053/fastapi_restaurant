from custom_select.select import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Restaurant
from db.model.category import Category
from src.vm.end.restaurant_vm import EndRestaurantGetReqModel, EndRestaurantRespModel


class GetRestaurant:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all_restaurant(self, params: EndRestaurantGetReqModel) -> tuple[list[EndRestaurantRespModel], int]:
        stmt = (
            select(Restaurant, Category.name.label("category_name"), func.count(Restaurant.id).over().label("total"))
            .select_from(Restaurant)
            .outerjoin(Category, Category.id == Restaurant.category_id)
            .where_if(params.name, lambda: Restaurant.name.ilike(f"%{params.name}%"))
            .where_if(params.tel, lambda: Restaurant.tel.ilike(f"%{params.tel}%"))
            .where_if(params.openingHours, lambda: Restaurant.openingHours.ilike(f"%{params.openingHours}%"))
            .where_if(params.address, lambda: Restaurant.address.ilike(f"%{params.address}%"))
            .where_if(params.description, lambda: Restaurant.description.ilike(f"%{params.description}%"))
            .offset((params.current_page - 1) * params.page_size)
            .limit(params.page_size)
        )
        results = await self._session.execute(stmt)

        results = results.fetchall()

        datas = [EndRestaurantRespModel.model_validate(result[0]).model_copy(
            update={"category_name": result[1]}
        ) for result in results]
        total = results[0][2] if results else 0

        return datas, total
