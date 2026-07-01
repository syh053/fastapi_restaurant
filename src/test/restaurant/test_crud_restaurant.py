from unittest.mock import AsyncMock, MagicMock

import pytest
from errors import Duplicate, Missing
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.end_service.restaurant_crud import CRUDRestaurant
from src.vm.end.restaurant_vm import EndRestaurantReqModel


class TestCrudRestaurant:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    async def service(self, mock_session: AsyncMock) -> CRUDRestaurant:
        return CRUDRestaurant(mock_session)

    @pytest.fixture
    def restaurant(self):
        return EndRestaurantReqModel(
            name="玉堂春魯肉飯",
            tel="04-23013008",
            openingHours=6,
            address="臺中市西區中興里美村路一段220號",
        )

    @pytest.fixture
    def mock_file(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.jpg"
        return file

    async def test_add_restaurant(self, service, restaurant: EndRestaurantReqModel, mock_file: MagicMock):
        service._save_file_to_folder = AsyncMock(return_value=mock_file)
        service._check_if_existed_restaurant = AsyncMock(return_value=False)

        await service.add_restaurant(restaurant=restaurant, file=mock_file)

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._check_if_existed_restaurant.assert_awaited_once_with("玉堂春魯肉飯")

        service._session.execute.assert_awaited_once()  # type: ignore
        service._session.commit.assert_awaited_once()  # type: ignore

    async def test_add_restaurant_with_error(
            self,
            service,
            restaurant: EndRestaurantReqModel,
            mock_file: MagicMock
    ):
        service._save_file_to_folder = AsyncMock(return_value=mock_file)
        service._check_if_existed_restaurant = AsyncMock(return_value=True)

        with pytest.raises(Duplicate):
            await service.add_restaurant(restaurant=restaurant, file=mock_file)

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._check_if_existed_restaurant.assert_awaited_once_with("玉堂春魯肉飯")

        # 不會進 DB 操作
        service._session.execute.assert_not_awaited()  # type: ignore
        service._session.commit.assert_not_awaited()  # type: ignore

    @pytest.mark.parametrize(
        "original_name", ["玉堂春魯肉飯"]
    )
    async def test_update_restaurant(
            self,
            service,
            original_name,
            restaurant: EndRestaurantReqModel,
            mock_file: MagicMock
    ):
        service._save_file_to_folder = AsyncMock(return_value=mock_file)
        service._check_if_existed_restaurant = AsyncMock(return_value=True)

        await service.update_restaurant(
            original_name=original_name,
            restaurant=restaurant,
            file=mock_file
        )

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._check_if_existed_restaurant.assert_awaited_once_with("玉堂春魯肉飯")

        service._session.execute.assert_awaited_once()  # type: ignore
        service._session.commit.assert_awaited_once()  # type: ignore

    @pytest.mark.parametrize(
        "original_name", ["玉堂春魯肉飯"]
    )
    async def test_update_restaurant_with_error(
            self,
            service,
            original_name,
            restaurant: EndRestaurantReqModel,
            mock_file: MagicMock
    ):
        service._save_file_to_folder = AsyncMock(return_value=mock_file)
        service._check_if_existed_restaurant = AsyncMock(return_value=False)

        with pytest.raises(Missing):
            await service.update_restaurant(
                original_name=original_name,
                restaurant=restaurant,
                file=mock_file
            )

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._check_if_existed_restaurant.assert_awaited_once_with("玉堂春魯肉飯")

        # 不會進 DB 操作
        service._session.execute.assert_not_awaited()  # type: ignore
        service._session.commit.assert_not_awaited()  # type: ignore

    @pytest.mark.parametrize(
        "name_list", [
            ["玉堂春魯肉飯", "李海魯肉飯", "財神爺魯肉飯"]
        ]
    )
    async def test_delete_restaurant(self, service, name_list: list[str]):
        service._check_if_existed_restaurant = AsyncMock(
            side_effect=[True, True, True]
        )
        await service.delete_restaurant(name_list)

    @pytest.mark.parametrize(
        "name_list", [
            ["玉堂春魯肉飯", "李海魯肉飯", "財神爺魯肉飯"]
        ]
    )
    async def test_delete_restaurant_with_error(self, service, name_list: list[str]):
        service._check_if_existed_restaurant = AsyncMock(
            side_effect=[True, True, False]
        )

        with pytest.raises(Missing):
            await service.delete_restaurant(name_list)
