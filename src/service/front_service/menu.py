from uuid import UUID

from custom_select.select import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import MenuItem
from src.vm.menu.menu_vm import MenuRespModel


class GetMenuService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_restaurant_menu(self, restaurant_id: UUID) -> list[MenuRespModel]:
        """
        取得指定餐廳的完整菜單（前台，不分頁）

        :param restaurant_id: 餐廳 ID
        :return: 依分區排序、分區、餐點名稱排序的餐點列表
        """
        stmt = (
            select(MenuItem)
            .where(MenuItem.restaurant_id == restaurant_id)
            .order_by(MenuItem.section_order, MenuItem.section, MenuItem.name)
        )
        results = await self._session.execute(stmt)
        results = results.scalars().all()

        return [MenuRespModel.model_validate(menu_item) for menu_item in results]
