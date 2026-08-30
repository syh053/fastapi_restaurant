from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from database_errors.errors import Duplicate, Missing
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.end_service.menu_crud import CRUDMenuService
from src.vm.menu.menu_vm import MenuReqModel, MenuRespModel

RESTAURANT_ID = UUID("11111111-1111-1111-1111-111111111111")
MENU_ITEM_ID = UUID("22222222-2222-2222-2222-222222222222")


def _menu_row(**overrides) -> SimpleNamespace:
    """模擬 RETURNING 取回的 MenuItem 資料列（可被 MenuRespModel.model_validate 接受）"""
    data = dict(
        id=MENU_ITEM_ID,
        restaurant_id=RESTAURANT_ID,
        name="玉堂春魯肉飯",
        price=180,
        section="主餐",
        section_order=0,
        description=None,
        image=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    data.update(overrides)
    return SimpleNamespace(**data)


class TestCRUDMenuService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        # execute() 回傳的 Result 為同步物件，需明確用 MagicMock（否則 AsyncMock 的子 mock
        # 會讓 result.scalar_one() 變成 coroutine）
        execute_result = MagicMock()
        execute_result.scalar_one.return_value = _menu_row()  # INSERT / UPDATE ... RETURNING
        execute_result.scalars.return_value.all.return_value = [_menu_row()]  # DELETE ... RETURNING
        session.execute = AsyncMock(return_value=execute_result)
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> CRUDMenuService:
        return CRUDMenuService(mock_session)

    @pytest.fixture
    def menu(self) -> MenuReqModel:
        return MenuReqModel(
            restaurant_id=RESTAURANT_ID,
            name="玉堂春魯肉飯",
            price=180,
            section="主餐",
        )

    @pytest.fixture
    def mock_file(self) -> MagicMock:
        file = MagicMock(spec=UploadFile)
        file.filename = "test.jpg"
        return file

    async def test_add_menu(
            self,
            service: CRUDMenuService,
            menu: MenuReqModel,
            mock_file: MagicMock,
    ):
        service._save_file_to_folder = AsyncMock(return_value=None)
        service._check_if_existed_restaurant = AsyncMock(return_value=True)
        service._check_if_duplicated_menu = AsyncMock(return_value=False)

        result = await service.add_menu(menu=menu, file=mock_file)

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._check_if_existed_restaurant.assert_awaited_once_with(service._session, menu.restaurant_id)
        service._check_if_duplicated_menu.assert_awaited_once_with(menu.restaurant_id, menu.name)
        service._session.execute.assert_awaited_once()  # type: ignore

        assert result["code"] == 200
        assert isinstance(result["data"], MenuRespModel)

    async def test_add_menu_with_section_order(
            self,
            service: CRUDMenuService,
            mock_session: AsyncMock,
    ):
        service._save_file_to_folder = AsyncMock(return_value=None)
        service._check_if_existed_restaurant = AsyncMock(return_value=True)
        service._check_if_duplicated_menu = AsyncMock(return_value=False)

        menu = MenuReqModel(
            restaurant_id=RESTAURANT_ID,
            name="頂級套餐",
            price=680,
            section="套餐",
            section_order=1,
        )
        await service.add_menu(menu=menu, file=None)

        stmt = mock_session.execute.call_args[0][0]
        assert stmt.compile().params["section_order"] == 1

    async def test_add_menu_restaurant_missing(
            self,
            service: CRUDMenuService,
            menu: MenuReqModel,
    ):
        service._check_if_existed_restaurant = AsyncMock(return_value=False)

        with pytest.raises(Missing):
            await service.add_menu(menu=menu, file=None)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_add_menu_duplicate(
            self,
            service: CRUDMenuService,
            menu: MenuReqModel,
    ):
        service._check_if_existed_restaurant = AsyncMock(return_value=True)
        service._check_if_duplicated_menu = AsyncMock(return_value=True)

        with pytest.raises(Duplicate):
            await service.add_menu(menu=menu, file=None)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_update_menu(
            self,
            service: CRUDMenuService,
            menu: MenuReqModel,
            mock_file: MagicMock,
    ):
        service._save_file_to_folder = AsyncMock(return_value=None)
        service._check_if_existed_menu_item = AsyncMock(return_value=True)

        result = await service.update_menu(menu_item_id=MENU_ITEM_ID, menu=menu, file=mock_file)

        service._save_file_to_folder.assert_awaited_once_with(file=mock_file)
        service._check_if_existed_menu_item.assert_awaited_once_with(service._session, MENU_ITEM_ID)
        service._session.execute.assert_awaited_once()  # type: ignore

        assert result["code"] == 200
        assert isinstance(result["data"], MenuRespModel)

    async def test_update_menu_missing(
            self,
            service: CRUDMenuService,
            menu: MenuReqModel,
    ):
        service._check_if_existed_menu_item = AsyncMock(return_value=False)

        with pytest.raises(Missing):
            await service.update_menu(menu_item_id=MENU_ITEM_ID, menu=menu, file=None)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_delete_menu(self, service: CRUDMenuService):
        service._check_if_existed_menu_item = AsyncMock(side_effect=[True, True, True])

        result = await service.delete_menu(menu_item_id_list=[uuid4(), uuid4(), uuid4()])

        service._session.execute.assert_awaited_once()  # type: ignore
        assert result["code"] == 200
        assert isinstance(result["data"], list)

    async def test_delete_menu_with_error(self, service: CRUDMenuService):
        service._check_if_existed_menu_item = AsyncMock(side_effect=[True, True, False])

        with pytest.raises(Missing):
            await service.delete_menu(menu_item_id_list=[uuid4(), uuid4(), uuid4()])

        service._session.execute.assert_not_awaited()  # type: ignore
