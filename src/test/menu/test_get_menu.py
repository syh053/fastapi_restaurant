from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.service.end_service.menu import GetMenuService as EndGetMenuService
from src.service.front_service.menu import GetMenuService as FrontGetMenuService
from src.vm.menu.menu_vm import MenuGetReqModel, MenuRespModel

RESTAURANT_ID = UUID("11111111-1111-1111-1111-111111111111")
MENU_ITEM_ID = UUID("22222222-2222-2222-2222-222222222222")


def _menu_item(name: str = "玉堂春魯肉飯", section: str = "主餐", section_order: int = 0) -> SimpleNamespace:
    """模擬查詢結果中的 MenuItem 物件（service 會讀取 __dict__ / 屬性）"""
    return SimpleNamespace(
        id=MENU_ITEM_ID,
        restaurant_id=RESTAURANT_ID,
        name=name,
        price=180,
        section=section,
        section_order=section_order,
        description=None,
        image=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


class TestEndGetMenuService:
    @staticmethod
    def _service(rows: list) -> EndGetMenuService:
        session = MagicMock(spec=AsyncSession)
        execute_result = MagicMock()
        execute_result.all.return_value = rows
        session.execute = AsyncMock(return_value=execute_result)
        return EndGetMenuService(session)

    async def test_get_all_menu(self):
        rows = [
            (_menu_item("A 套餐", "主餐"), "鼎泰豐", 2),
            (_menu_item("B 湯品", "湯品"), "鼎泰豐", 2),
        ]
        service = self._service(rows)

        datas, total = await service.get_all_menu(
            MenuGetReqModel(restaurant_id=RESTAURANT_ID, current_page=1, page_size=10)
        )

        assert total == 2
        assert all(isinstance(item, MenuRespModel) for item in datas)
        assert [item.name for item in datas] == ["A 套餐", "B 湯品"]
        # join 帶出的餐廳名稱
        assert datas[0].restaurant_name == "鼎泰豐"

    async def test_get_all_menu_order_by_section_order(self):
        """後台列表排序鍵應為 section_order -> section -> name"""
        service = self._service([])

        await service.get_all_menu(MenuGetReqModel())

        compiled = str(service._session.execute.call_args[0][0])  # type: ignore
        order_by = compiled.split("ORDER BY")[1]
        assert order_by.index("section_order") < order_by.index("menu_item.section,") < order_by.index("menu_item.name")

    async def test_get_all_menu_empty(self):
        service = self._service([])

        datas, total = await service.get_all_menu(MenuGetReqModel())

        assert datas == []
        assert total == 0


class TestFrontGetMenuService:
    async def test_get_restaurant_menu(self):
        session = MagicMock(spec=AsyncSession)
        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = [
            _menu_item("前菜拼盤", "前菜"),
            _menu_item("招牌牛肉麵", "主餐"),
        ]
        session.execute = AsyncMock(return_value=execute_result)
        service = FrontGetMenuService(session)

        menu = await service.get_restaurant_menu(RESTAURANT_ID)

        assert all(isinstance(item, MenuRespModel) for item in menu)
        assert [item.name for item in menu] == ["前菜拼盤", "招牌牛肉麵"]
        assert all(item.restaurant_id == RESTAURANT_ID for item in menu)

    async def test_get_restaurant_menu_order_by_section_order(self):
        """前台菜單排序鍵應為 section_order -> section -> name"""
        session = MagicMock(spec=AsyncSession)
        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=execute_result)
        service = FrontGetMenuService(session)

        await service.get_restaurant_menu(RESTAURANT_ID)

        compiled = str(session.execute.call_args[0][0])
        order_by = compiled.split("ORDER BY")[1]
        assert order_by.index("section_order") < order_by.index("menu_item.section,") < order_by.index("menu_item.name")
