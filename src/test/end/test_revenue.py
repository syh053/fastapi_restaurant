from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.end_service.revenue import RevenueService
from src.vm.end.revenue_vm import RevenueGetReqModel

OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")
RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")


def _result(rows) -> MagicMock:
    result = MagicMock()
    result.all.return_value = rows
    return result


class TestRevenueService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> RevenueService:
        return RevenueService(mock_session)

    async def test_get_revenue(self, service: RevenueService, mock_session: AsyncMock):
        daily = [
            SimpleNamespace(date=date(2026, 10, 1), order_count=2, revenue=500),
            SimpleNamespace(date=date(2026, 10, 2), order_count=1, revenue=300),
        ]
        restaurants = [SimpleNamespace(id=RESTAURANT_ID, name="好吃餐廳", order_count=3, revenue=800)]
        mock_session.execute.side_effect = [_result(daily), _result(restaurants)]

        result = await service.get_revenue(OWNER_ID, RevenueGetReqModel())

        assert result.total_revenue == 800
        assert result.total_orders == 3
        assert [d.revenue for d in result.daily] == [500, 300]
        assert result.restaurants[0].restaurant_name == "好吃餐廳"

    async def test_get_revenue_empty(self, service: RevenueService, mock_session: AsyncMock):
        mock_session.execute.side_effect = [_result([]), _result([])]

        result = await service.get_revenue(OWNER_ID, RevenueGetReqModel())

        assert result.total_revenue == 0
        assert result.total_orders == 0
        assert result.daily == []

    async def test_get_revenue_restaurant_not_owned(self, service: RevenueService, mock_session: AsyncMock):
        not_found = MagicMock()
        not_found.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = not_found

        with pytest.raises(Missing):
            await service.get_revenue(OWNER_ID, RevenueGetReqModel(restaurant_id=RESTAURANT_ID))

        mock_session.execute.assert_awaited_once()
