from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.cart.get_cart import GetCartService
from src.vm.cart.cart_vm import CartItemRespModel, CartRespModel

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")
CART_ITEM_ID = UUID("33333333-3333-3333-3333-333333333333")
MENU_ITEM_ID = UUID("44444444-4444-4444-4444-444444444444")


def _cart_row(**overrides) -> SimpleNamespace:
    """模擬 Cart 與 MenuItem/Restaurant join 查詢後取回的一列（Row，具備 ._mapping）"""
    data = dict(
        id=CART_ITEM_ID,
        quantity=2,
        menu_item_id=MENU_ITEM_ID,
        name="玉堂春魯肉飯",
        price=180,
        image=None,
        restaurant_id=RESTAURANT_ID,
        restaurant_name="鼎泰豐",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    data.update(overrides)
    row = SimpleNamespace(**data)
    row._mapping = data
    return row


class TestGetCartService:
    @staticmethod
    def _service(rows: list) -> GetCartService:
        session = MagicMock(spec=AsyncSession)
        execute_result = MagicMock()
        execute_result.all.return_value = rows
        session.execute = AsyncMock(return_value=execute_result)
        return GetCartService(session)

    async def test_get_cart(self):
        rows = [
            _cart_row(name="玉堂春魯肉飯", price=180, quantity=2),
            _cart_row(id=UUID("55555555-5555-5555-5555-555555555555"), name="貢丸湯", price=40, quantity=1),
        ]
        service = self._service(rows)

        items, total = await service.get_cart(USER_ID)

        assert all(isinstance(item, CartItemRespModel) for item in items)
        assert [item.subtotal for item in items] == [360, 40]
        assert total == 400

    async def test_get_cart_empty(self):
        service = self._service([])

        items, total = await service.get_cart(USER_ID)

        assert items == []
        assert total == 0

    async def test_get_cart_response(self):
        service = self._service([_cart_row()])

        response = await service.get_cart_response(USER_ID)

        assert response["code"] == 200
        assert isinstance(response["data"], CartRespModel)
        assert response["data"].total == 360
        assert len(response["data"].items) == 1
