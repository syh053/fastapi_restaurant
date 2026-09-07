from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from database_errors.errors import Duplicate, Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.cart.get_cart import CRUDCartService
from src.vm.cart.cart_vm import CartItemReqModel, CartRespModel

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
RESTAURANT_ID = UUID("22222222-2222-2222-2222-222222222222")
OTHER_RESTAURANT_ID = UUID("33333333-3333-3333-3333-333333333333")
MENU_ITEM_ID = UUID("44444444-4444-4444-4444-444444444444")
CART_ITEM_ID = UUID("55555555-5555-5555-5555-555555555555")


def _menu_item(**overrides) -> SimpleNamespace:
    data = dict(id=MENU_ITEM_ID, restaurant_id=RESTAURANT_ID, name="玉堂春魯肉飯", price=180)
    data.update(overrides)
    return SimpleNamespace(**data)


def _cart_item(**overrides) -> SimpleNamespace:
    data = dict(id=CART_ITEM_ID, user_id=USER_ID, menu_item_id=MENU_ITEM_ID, quantity=2)
    data.update(overrides)
    return SimpleNamespace(**data)


class TestCRUDCartService:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session: AsyncMock) -> CRUDCartService:
        svc = CRUDCartService(mock_session)
        svc._get_service.get_cart_response = AsyncMock(
            return_value={"code": 200, "message": "查詢購物車成功!", "data": CartRespModel(items=[], total=0)}
        )
        return svc

    # --- add_to_cart ---

    async def test_add_new_item(self, service: CRUDCartService):
        service._get_menu_item = AsyncMock(return_value=_menu_item())
        service._get_cart_restaurant_id = AsyncMock(return_value=None)
        service._get_cart_item_by_menu = AsyncMock(return_value=None)

        item = CartItemReqModel(menu_item_id=MENU_ITEM_ID, quantity=1)
        result = await service.add_to_cart(user_id=USER_ID, item=item, clear_existing=False)

        service._session.execute.assert_awaited_once()  # type: ignore
        stmt = str(service._session.execute.call_args[0][0])  # type: ignore
        assert "INSERT INTO restaurant.cart" in stmt
        assert result["code"] == 200
        assert isinstance(result["data"], CartRespModel)

    async def test_add_existing_item_merges_quantity(self, service: CRUDCartService):
        service._get_menu_item = AsyncMock(return_value=_menu_item())
        service._get_cart_restaurant_id = AsyncMock(return_value=RESTAURANT_ID)
        service._get_cart_item_by_menu = AsyncMock(return_value=_cart_item(quantity=2))

        item = CartItemReqModel(menu_item_id=MENU_ITEM_ID, quantity=3)
        await service.add_to_cart(user_id=USER_ID, item=item, clear_existing=False)

        stmt = str(service._session.execute.call_args[0][0])  # type: ignore
        assert "UPDATE restaurant.cart" in stmt
        assert service._session.execute.call_args[0][0].compile().params["quantity"] == 5  # type: ignore

    async def test_add_menu_item_missing(self, service: CRUDCartService):
        service._get_menu_item = AsyncMock(return_value=None)

        item = CartItemReqModel(menu_item_id=MENU_ITEM_ID, quantity=1)
        with pytest.raises(Missing):
            await service.add_to_cart(user_id=USER_ID, item=item, clear_existing=False)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_add_conflict_different_restaurant(self, service: CRUDCartService):
        service._get_menu_item = AsyncMock(return_value=_menu_item(restaurant_id=RESTAURANT_ID))
        service._get_cart_restaurant_id = AsyncMock(return_value=OTHER_RESTAURANT_ID)

        item = CartItemReqModel(menu_item_id=MENU_ITEM_ID, quantity=1)
        with pytest.raises(Duplicate):
            await service.add_to_cart(user_id=USER_ID, item=item, clear_existing=False)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_add_conflict_clears_existing_when_requested(self, service: CRUDCartService):
        service._get_menu_item = AsyncMock(return_value=_menu_item(restaurant_id=RESTAURANT_ID))
        service._get_cart_restaurant_id = AsyncMock(return_value=OTHER_RESTAURANT_ID)
        service._get_cart_item_by_menu = AsyncMock(return_value=None)

        item = CartItemReqModel(menu_item_id=MENU_ITEM_ID, quantity=1)
        await service.add_to_cart(user_id=USER_ID, item=item, clear_existing=True)

        assert service._session.execute.await_count == 2  # type: ignore
        delete_stmt = str(service._session.execute.call_args_list[0][0][0])  # type: ignore
        insert_stmt = str(service._session.execute.call_args_list[1][0][0])  # type: ignore
        assert "DELETE FROM restaurant.cart" in delete_stmt
        assert "INSERT INTO restaurant.cart" in insert_stmt

    # --- update_quantity ---

    async def test_update_quantity(self, service: CRUDCartService):
        service._get_cart_item_by_id = AsyncMock(return_value=_cart_item())

        result = await service.update_quantity(user_id=USER_ID, cart_item_id=CART_ITEM_ID, quantity=5)

        service._session.execute.assert_awaited_once()  # type: ignore
        assert result["code"] == 200

    async def test_update_quantity_missing(self, service: CRUDCartService):
        service._get_cart_item_by_id = AsyncMock(return_value=None)

        with pytest.raises(Missing):
            await service.update_quantity(user_id=USER_ID, cart_item_id=CART_ITEM_ID, quantity=5)

        service._session.execute.assert_not_awaited()  # type: ignore

    # --- remove_from_cart ---

    async def test_remove_from_cart(self, service: CRUDCartService):
        service._get_cart_item_by_id = AsyncMock(return_value=_cart_item())

        result = await service.remove_from_cart(user_id=USER_ID, cart_item_id=CART_ITEM_ID)

        service._session.execute.assert_awaited_once()  # type: ignore
        assert result["code"] == 200

    async def test_remove_from_cart_missing(self, service: CRUDCartService):
        service._get_cart_item_by_id = AsyncMock(return_value=None)

        with pytest.raises(Missing):
            await service.remove_from_cart(user_id=USER_ID, cart_item_id=CART_ITEM_ID)

        service._session.execute.assert_not_awaited()  # type: ignore

    async def test_remove_from_cart_not_owned(self, service: CRUDCartService):
        """不屬於該使用者的購物車品項應視為不存在（避免洩漏其他使用者的購物車內容）"""
        service._get_cart_item_by_id = AsyncMock(return_value=None)

        with pytest.raises(Missing):
            await service.remove_from_cart(user_id=USER_ID, cart_item_id=uuid4())

        service._session.execute.assert_not_awaited()  # type: ignore

    # --- clear_cart ---

    async def test_clear_cart(self, service: CRUDCartService):
        result = await service.clear_cart(user_id=USER_ID)

        service._session.execute.assert_awaited_once()  # type: ignore
        stmt = str(service._session.execute.call_args[0][0])  # type: ignore
        assert "DELETE FROM restaurant.cart" in stmt
        assert result["code"] == 200
        assert result["data"].items == []
        assert result["data"].total == 0
