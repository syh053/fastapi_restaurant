from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from db.model.database import get_session
from src.service.end_service.restaurant import GetRestaurant
from src.vm.end_restaurant.restaurant_vm import EndRestaurantGetReqModel, EndRestaurantRespModel


class TestGetRestaurant:
    @pytest.fixture
    async def service(self):
        async for session in get_session():
            yield GetRestaurant(session)

    @pytest.mark.parametrize(
        "params", [
            EndRestaurantGetReqModel(
                name=None,
                tel=None,
                openingHours=None,
                address=None,
                description=None,
                current_page=1,
                page_size=10
            )
        ]
    )
    async def test_get_all_restaurant(self, service: GetRestaurant, params: EndRestaurantGetReqModel):
        """
        測試餐廳列表功能

        :param service: 提供 GetRestaurant Service
        :param params: 搜尋餐廳列表參數
        :return: 餐廳列表及數量
        """
        results = await service.get_all_restaurant(params)

        assert isinstance(results[0], list)
        assert isinstance(results[0][0], EndRestaurantRespModel)
        assert isinstance(results[1], int)
