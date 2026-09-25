from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.order.pay import OrderPayService

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
OTHER_USER_ID = UUID("99999999-9999-9999-9999-999999999999")
ORDER_ID = UUID("22222222-2222-2222-2222-222222222222")


def _order(**overrides) -> SimpleNamespace:
    data = dict(
        id=ORDER_ID,
        user_id=USER_ID,
        status="pending",
        merchant_trade_no="original0000000001",
        total_amount=220,
    )
    data.update(overrides)
    return SimpleNamespace(**data)


class TestOrderPayService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> OrderPayService:
        return OrderPayService(mock_session)

    async def test_build_pay_form_regenerates_merchant_trade_no(
            self, service: OrderPayService, mock_session: AsyncMock
    ):
        order = _order()
        original_trade_no = order.merchant_trade_no
        service._get_order_by_id = AsyncMock(return_value=order)
        service._get_order_items = AsyncMock(return_value=[])

        result = await service.build_pay_form(user_id=USER_ID, order_id=ORDER_ID)

        assert order.merchant_trade_no != original_trade_no
        assert result["fields"]["MerchantTradeNo"] == order.merchant_trade_no
        mock_session.execute.assert_awaited_once()
        stmt = mock_session.execute.call_args[0][0]
        assert stmt.compile().params["merchant_trade_no"] == order.merchant_trade_no

    async def test_build_pay_form_order_not_found(self, service: OrderPayService, mock_session: AsyncMock):
        service._get_order_by_id = AsyncMock(return_value=None)

        with pytest.raises(Missing):
            await service.build_pay_form(user_id=USER_ID, order_id=ORDER_ID)

        mock_session.execute.assert_not_awaited()

    async def test_build_pay_form_not_owned(self, service: OrderPayService, mock_session: AsyncMock):
        service._get_order_by_id = AsyncMock(return_value=_order(user_id=OTHER_USER_ID))

        with pytest.raises(Missing):
            await service.build_pay_form(user_id=USER_ID, order_id=ORDER_ID)

        mock_session.execute.assert_not_awaited()

    async def test_build_pay_form_not_pending(self, service: OrderPayService, mock_session: AsyncMock):
        service._get_order_by_id = AsyncMock(return_value=_order(status="paid"))

        with pytest.raises(Missing):
            await service.build_pay_form(user_id=USER_ID, order_id=ORDER_ID)

        mock_session.execute.assert_not_awaited()
