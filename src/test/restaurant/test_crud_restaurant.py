from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from database_errors.errors import Duplicate, Missing

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.end_service.restaurant_crud import CRUDRestaurant
from src.vm.end.restaurant_vm import EndRestaurantReqModel


class TestCrudRestaurant:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
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
            address="臺中市西區中興里美村路一段220號"
        )

    @pytest.fixture
    def mock_file(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.jpg"
        return file

    async def test_add_restaurant(
            self,
            service: CRUDRestaurant,
            restaurant: EndRestaurantReqModel,
            mock_file: MagicMock
    ):
        service._save_file_to_folder = AsyncMock(return_value=mock_file)
        service._check_if_existed_restaurant = AsyncMock(return_value=False)
        service._get_default_category_id = AsyncMock(return_value=UUID("089b94d1-1129-4e1a-8d29-4683d2e9004b"))

        await service.add_restaurant(restaurant=restaurant, file=mock_file)

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._check_if_existed_restaurant.assert_awaited_once_with("玉堂春魯肉飯")

        service._session.execute.assert_awaited_once()  # type: ignore


    async def test_add_restaurant_with_error(
            self,
            service: CRUDRestaurant,
            restaurant: EndRestaurantReqModel,
            mock_file: MagicMock
    ):
        service._save_file_to_folder = AsyncMock(return_value=mock_file)
        service._check_if_existed_restaurant = AsyncMock(return_value=True)
        service._get_default_category_id = AsyncMock(return_value=UUID("089b94d1-1129-4e1a-8d29-4683d2e9004b"))

        with pytest.raises(Duplicate):
            await service.add_restaurant(restaurant=restaurant, file=mock_file)

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._check_if_existed_restaurant.assert_awaited_once_with("玉堂春魯肉飯")

        # 不會進 DB 操作
        service._session.execute.assert_not_awaited()  # type: ignore


    @pytest.mark.parametrize(
        "original_name", ["玉堂春魯肉飯"]
    )
    async def test_update_restaurant(
            self,
            service: CRUDRestaurant,
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


    @pytest.mark.parametrize(
        "original_name", ["玉堂春魯肉飯"]
    )
    async def test_update_restaurant_with_error(
            self,
            service: CRUDRestaurant,
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

    @pytest.mark.parametrize(
        "name_list", [
            ["玉堂春魯肉飯", "李海魯肉飯", "財神爺魯肉飯"]
        ]
    )
    async def test_delete_restaurant(self, service: CRUDRestaurant, name_list: list[str]):
        service._check_if_existed_restaurant = AsyncMock(
            side_effect=[True, True, True]
        )
        await service.delete_restaurant(name_list)

    @pytest.mark.parametrize(
        "name_list", [
            ["玉堂春魯肉飯", "李海魯肉飯", "財神爺魯肉飯"]
        ]
    )
    async def test_delete_restaurant_with_error(self, service: CRUDRestaurant, name_list: list[str]):
        service._check_if_existed_restaurant = AsyncMock(
            side_effect=[True, True, False]
        )

        with pytest.raises(Missing):
            await service.delete_restaurant(name_list)

    async def test_add_restaurant_with_provided_category_id(
            self,
            service: CRUDRestaurant,
            mock_file: MagicMock,
    ):
        """帶入 category_id 時，不應查詢預設分類"""
        service._save_file_to_folder = AsyncMock(return_value=mock_file)
        service._check_if_existed_restaurant = AsyncMock(return_value=False)
        service._get_default_category_id = AsyncMock()

        restaurant = EndRestaurantReqModel(
            name="玉堂春魯肉飯",
            tel="04-23013008",
            openingHours=6,
            address="臺中市西區中興里美村路一段220號",
            category_id=UUID("089b94d1-1129-4e1a-8d29-4683d2e9004b")
        )
        await service.add_restaurant(restaurant=restaurant, file=None)

        service._get_default_category_id.assert_not_awaited()
        service._save_file_to_folder.assert_not_awaited()

    # --- _get_default_category_id ---

    async def test_get_default_category_id(self, service: CRUDRestaurant, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = UUID("089b94d1-1129-4e1a-8d29-4683d2e9004b")
        mock_session.execute.return_value = execute_result

        result = await service._get_default_category_id()

        assert result == UUID("089b94d1-1129-4e1a-8d29-4683d2e9004b")

    async def test_get_default_category_id_missing(self, service: CRUDRestaurant, mock_session: AsyncMock):
        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = execute_result

        result = await service._get_default_category_id()

        assert result is None

    # --- _save_file_to_folder ---

    @pytest.fixture
    def patched_restaurant_path(self, tmp_path, monkeypatch):
        import src.service.end_service.restaurant_crud as module
        monkeypatch.setattr(module, "restaurant_path", tmp_path)
        return tmp_path

    async def test_save_file_to_folder(self, service: CRUDRestaurant, mock_file: MagicMock, patched_restaurant_path):
        mock_file.read = AsyncMock(side_effect=[b"content", b""])
        mock_file.close = AsyncMock()

        await service._save_file_to_folder(file=mock_file)

        assert (patched_restaurant_path / mock_file.filename).exists()
        mock_file.close.assert_awaited_once()

    async def test_save_file_to_folder_write_failure(
            self, service: CRUDRestaurant, mock_file: MagicMock, patched_restaurant_path
    ):
        mock_file.read = AsyncMock(side_effect=OSError("disk full"))
        mock_file.close = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await service._save_file_to_folder(file=mock_file)

        assert exc_info.value.status_code == 500
        mock_file.close.assert_awaited_once()
