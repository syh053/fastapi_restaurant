from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.order.get_order import OrderGetService

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
OTHER_USER_ID = UUID("99999999-9999-9999-9999-999999999999")
RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")
ORDER_ID = UUID("33333333-3333-3333-3333-333333333333")


def _order(**overrides) -> SimpleNamespace:
    data = dict(
        id=ORDER_ID,
        user_id=USER_ID,
        restaurant_id=RESTAURANT_ID,
        status="pending",
        total_amount=360,
        merchant_trade_no="abc123",
        ecpay_trade_no=None,
        payment_date=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    data.update(overrides)
    return SimpleNamespace(**data)


class TestOrderGetService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> OrderGetService:
        return OrderGetService(mock_session)

    async def test_get_order_detail_response(self, service: OrderGetService):
        service._get_order_by_id = AsyncMock(return_value=_order())
        service._get_order_items = AsyncMock(return_value=[])

        response = await service.get_order_detail_response(user_id=USER_ID, order_id=ORDER_ID)

        assert response["code"] == 200
        assert response["data"].id == ORDER_ID
        assert response["data"].status == "pending"

    async def test_get_order_detail_not_found_raises_missing(self, service: OrderGetService):
        service._get_order_by_id = AsyncMock(return_value=None)

        with pytest.raises(Missing):
            await service.get_order_detail_response(user_id=USER_ID, order_id=ORDER_ID)

    async def test_get_order_detail_not_owned_raises_missing(self, service: OrderGetService):
        service._get_order_by_id = AsyncMock(return_value=_order(user_id=OTHER_USER_ID))

        with pytest.raises(Missing):
            await service.get_order_detail_response(user_id=USER_ID, order_id=ORDER_ID)

    async def test_get_order_list_response(self, service: OrderGetService):
        service._get_orders_by_user = AsyncMock(return_value=[_order(), _order(id=UUID("44444444-4444-4444-4444-444444444444"))])
        service._get_order_items = AsyncMock(return_value=[])

        response = await service.get_order_list_response(user_id=USER_ID)

        assert response["code"] == 200
        assert len(response["data"]) == 2
