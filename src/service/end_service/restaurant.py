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
        print("查詢參數 :", params)
        stmt = (
            select(Restaurant, Category.name.label("category_name"), func.count(Restaurant.id).over().label("total"))
            .select_from(Restaurant)
            .outerjoin(Category, Restaurant.category_id == Category.id)
            .where_if(params.name, lambda: Restaurant.name.ilike(f"%{params.name}%"))
            .where_if(params.category_name, lambda: Category.name.ilike(f"%{params.category_name}%"))
            .where_if(params.tel, lambda: Restaurant.tel.ilike(f"%{params.tel}%"))
            .where_if(params.openingHours, lambda: Restaurant.openingHours == params.openingHours)
            .where_if(params.address, lambda: Restaurant.address.ilike(f"%{params.address}%"))
            .where_if(params.description, lambda :Restaurant.description.ilike(f"%{params.description}%"))
            .offset((params.current_page - 1) * params.page_size)
            .limit(params.page_size)
        )
        results = await self._session.execute(stmt)

        results = results.all()

        datas = [
            EndRestaurantRespModel(
                **{
                    **result[0].__dict__,  # Restaurant 的欄位
                    "category_name": result[1],
                }
            )
            for result in results
        ]

        total = results[0][-1] if results else 0

        return datas, total

    async def get_category(self):
        stmt = (
            select(Category)
        )
        results = await self._session.execute(stmt)
        results = results.scalars().all()

        return results

