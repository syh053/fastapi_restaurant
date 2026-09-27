from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.restaurant import GetRestaurant
from src.vm.end.restaurant_vm import EndRestaurantGetReqModel, EndRestaurantRespModel

RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")
CATEGORY_ID = UUID("44444444-4444-4444-4444-444444444444")


def _restaurant(**overrides) -> SimpleNamespace:
    data = dict(
        id=RESTAURANT_ID,
        name="玉堂春魯肉飯",
        tel="04-23013008",
        openingHours=6,
        address="臺中市西區中興里美村路一段220號",
        description=None,
        image=None,
        category_id=CATEGORY_ID,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    data.update(overrides)
    return SimpleNamespace(**data)


def _category(**overrides) -> SimpleNamespace:
    data = dict(id=CATEGORY_ID, name="小吃")
    data.update(overrides)
    return SimpleNamespace(**data)


class TestFrontGetRestaurant:
    """
    前台餐廳查詢 GetRestaurant（src/service/front_service/restaurant.py），
    與 end_service 中同名的 GetRestaurant 為不同類別，需分開測試。
    """

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> GetRestaurant:
        return GetRestaurant(mock_session)

    @pytest.fixture
    def empty_params(self) -> EndRestaurantGetReqModel:
        return EndRestaurantGetReqModel(
            name=None,
            category_name=None,
            tel=None,
            openingHours=None,
            address=None,
            description=None,
            current_page=1,
            page_size=10
        )

    async def test_get_all_restaurant(
            self, service: GetRestaurant, mock_session: AsyncMock, empty_params: EndRestaurantGetReqModel
    ):
        execute_result = MagicMock()
        execute_result.fetchall.return_value = [(_restaurant(), "小吃", 1)]
        mock_session.execute.return_value = execute_result

        datas, total = await service.get_all_restaurant(empty_params)

        mock_session.execute.assert_awaited_once()
        assert isinstance(datas[0], EndRestaurantRespModel)
        assert datas[0].category_name == "小吃"
        assert total == 1

    async def test_get_all_restaurant_empty(
            self, service: GetRestaurant, mock_session: AsyncMock, empty_params: EndRestaurantGetReqModel
    ):
        execute_result = MagicMock()
        execute_result.fetchall.return_value = []
        mock_session.execute.return_value = execute_result

        datas, total = await service.get_all_restaurant(empty_params)

        assert datas == []
        assert total == 0

    async def test_get_category(self, service: GetRestaurant, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = [_category()]
        mock_session.execute.return_value = execute_result

        results = await service.get_category()

        mock_session.execute.assert_awaited_once()
        assert list(results) == [_category()]
