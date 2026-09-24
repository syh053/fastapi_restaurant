from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.payment.ecpay_notify import EcpayNotifyService

ORDER_ID = UUID("11111111-1111-1111-1111-111111111111")


def _order(**overrides) -> SimpleNamespace:
    data = dict(id=ORDER_ID, status="pending", merchant_trade_no="abc123")
    data.update(overrides)
    return SimpleNamespace(**data)


class TestEcpayNotifyService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> EcpayNotifyService:
        return EcpayNotifyService(mock_session)

    async def test_invalid_check_mac_value_rejected(self, service: EcpayNotifyService, mock_session: AsyncMock):
        with patch("src.service.payment.ecpay_notify.verify_notify_check_mac_value", return_value=False):
            result = await service.handle_notify({"MerchantTradeNo": "abc123", "RtnCode": "1"})

        assert result == "0|CheckMacValue Error"
        mock_session.execute.assert_not_awaited()

    async def test_order_not_found(self, service: EcpayNotifyService, mock_session: AsyncMock):
        service._get_order_by_merchant_trade_no = AsyncMock(return_value=None)

        with patch("src.service.payment.ecpay_notify.verify_notify_check_mac_value", return_value=True):
            result = await service.handle_notify({"MerchantTradeNo": "not-exist", "RtnCode": "1"})

        assert result == "0|Order Not Found"
        mock_session.execute.assert_not_awaited()

    async def test_payment_success_updates_order_to_paid(self, service: EcpayNotifyService, mock_session: AsyncMock):
        service._get_order_by_merchant_trade_no = AsyncMock(return_value=_order(status="pending"))

        with patch("src.service.payment.ecpay_notify.verify_notify_check_mac_value", return_value=True):
            result = await service.handle_notify({
                "MerchantTradeNo": "abc123",
                "RtnCode": "1",
                "TradeNo": "2026010112345678",
                "PaymentDate": "2026/01/01 12:00:00",
            })

        assert result == "1|OK"
        mock_session.execute.assert_awaited_once()
        stmt = str(mock_session.execute.call_args[0][0])
        assert "UPDATE restaurant.\"order\"" in stmt or "UPDATE restaurant.order" in stmt

    async def test_payment_failure_marks_order_failed(self, service: EcpayNotifyService, mock_session: AsyncMock):
        service._get_order_by_merchant_trade_no = AsyncMock(return_value=_order(status="pending"))

        with patch("src.service.payment.ecpay_notify.verify_notify_check_mac_value", return_value=True):
            result = await service.handle_notify({"MerchantTradeNo": "abc123", "RtnCode": "10100058"})

        assert result == "1|OK"
        mock_session.execute.assert_awaited_once()
        stmt = mock_session.execute.call_args[0][0]
        assert stmt.compile().params["status"] == "failed"

    async def test_already_paid_order_is_idempotent(self, service: EcpayNotifyService, mock_session: AsyncMock):
        service._get_order_by_merchant_trade_no = AsyncMock(return_value=_order(status="paid"))

        with patch("src.service.payment.ecpay_notify.verify_notify_check_mac_value", return_value=True):
            result = await service.handle_notify({"MerchantTradeNo": "abc123", "RtnCode": "1"})

        assert result == "1|OK"
        mock_session.execute.assert_not_awaited()
