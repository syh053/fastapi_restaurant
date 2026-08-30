from custom_select.select import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import MenuItem, Restaurant
from src.vm.menu.menu_vm import MenuGetReqModel, MenuRespModel


class GetMenuService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all_menu(self, params: MenuGetReqModel) -> tuple[list[MenuRespModel], int]:
        """
        取得餐點列表

        :param params: 查詢與分頁參數
        :return: (餐點列表, 總筆數)
        """
        stmt = (
            select(
                MenuItem,
                Restaurant.name.label("restaurant_name"),
                func.count(MenuItem.id).over().label("total"),
            )
            .select_from(MenuItem)
            .outerjoin(Restaurant, Restaurant.id == MenuItem.restaurant_id)
            .where_if(params.name, lambda: MenuItem.name.ilike(f"%{params.name}%"))
            .where_if(params.section, lambda: MenuItem.section.ilike(f"%{params.section}%"))
            .where_if(params.restaurant_id, lambda: MenuItem.restaurant_id == params.restaurant_id)
            .order_by(MenuItem.section_order, MenuItem.section, MenuItem.name)
            .offset((params.current_page - 1) * params.page_size)
            .limit(params.page_size)
        )
        results = await self._session.execute(stmt)
        results = results.all()

        datas = [
            MenuRespModel(
                **{
                    **result[0].__dict__,  # MenuItem 的欄位
                    "restaurant_name": result[1],
                }
            )
            for result in results
        ]

        total = results[0][-1] if results else 0

        return datas, total
