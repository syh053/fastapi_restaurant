from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.order.checkout import OrderCheckoutService
from src.vm.cart.cart_vm import CartItemRespModel
from src.vm.order.order_vm import CheckoutRespModel

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")
MENU_ITEM_ID = UUID("33333333-3333-3333-3333-333333333333")
ORDER_ID = UUID("44444444-4444-4444-4444-444444444444")


def _cart_item(**overrides) -> CartItemRespModel:
    data = dict(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        menu_item_id=MENU_ITEM_ID,
        name="玉堂春魯肉飯",
        price=180,
        quantity=2,
        subtotal=360,
        image=None,
        restaurant_id=RESTAURANT_ID,
        restaurant_name="鼎泰豐",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    data.update(overrides)
    return CartItemRespModel(**data)


def _order_row(**overrides) -> SimpleNamespace:
    data = dict(
        id=ORDER_ID,
        status="pending",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    data.update(overrides)
    return SimpleNamespace(**data)


def _order_item_row(**overrides) -> SimpleNamespace:
    data = dict(
        id=UUID("66666666-6666-6666-6666-666666666666"),
        menu_item_id=MENU_ITEM_ID,
        name="玉堂春魯肉飯",
        unit_price=180,
        quantity=2,
        subtotal=360,
    )
    data.update(overrides)
    row = SimpleNamespace(**data)
    row._mapping = data
    return row


class TestOrderCheckoutService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> OrderCheckoutService:
        return OrderCheckoutService(mock_session)

    async def test_checkout_success(self, service: OrderCheckoutService, mock_session: AsyncMock):
        service.get_cart = AsyncMock(return_value=([_cart_item()], 360))

        order_execute_result = MagicMock()
        order_execute_result.one.return_value = _order_row()
        item_execute_result = MagicMock()
        item_execute_result.all.return_value = [_order_item_row()]
        delete_execute_result = MagicMock()

        mock_session.execute.side_effect = [
            order_execute_result,
            item_execute_result,
            delete_execute_result,
        ]

        result = await service.checkout(user_id=USER_ID)

        assert result["code"] == 200
        assert isinstance(result["data"], CheckoutRespModel)
        assert result["data"].order.total_amount == 360
        assert result["data"].order.status == "pending"
        assert len(result["data"].order.items) == 1
        assert result["data"].pay_url == f"/front/order/{ORDER_ID}/pay"

        assert mock_session.execute.await_count == 3
        insert_stmt = str(mock_session.execute.call_args_list[0][0][0])
        assert "INSERT INTO restaurant.\"order\"" in insert_stmt or "INSERT INTO restaurant.order" in insert_stmt
        delete_stmt = str(mock_session.execute.call_args_list[2][0][0])
        assert "DELETE FROM restaurant.cart" in delete_stmt

    async def test_checkout_empty_cart_raises_missing(self, service: OrderCheckoutService, mock_session: AsyncMock):
        service.get_cart = AsyncMock(return_value=([], 0))

        with pytest.raises(Missing):
            await service.checkout(user_id=USER_ID)

        mock_session.execute.assert_not_awaited()
