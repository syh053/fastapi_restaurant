from uuid import UUID

from database_errors.errors import Missing, Duplicate
from sqlalchemy import delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Cart
from src.service.basic.basic_service import BasicService
from src.service.front_service.cart.get_cart import CartGetService
from src.vm.cart.cart_vm import CartItemReqModel


class CartCreateService(BasicService, CartGetService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def add_to_cart(self, user_id: UUID, item: CartItemReqModel, clear_existing: bool) -> dict:
        """
        加入購物車功能，若餐點已在購物車中則累加數量；若購物車已有其他餐廳的餐點，
        預設拒絕加入，可帶 clear_existing=True 清空原有品項後再加入。

        :param user_id: 使用者 ID
        :param item: 欲加入的餐點與數量
        :param clear_existing: 是否清空購物車內其他餐廳的既有品項
        :return: 回傳加入成功訊息與最新購物車內容
        """
        menu_item = await self._get_menu_item(item.menu_item_id)
        if menu_item is None:
            raise Missing(msg="餐點不存在")

        existing_restaurant_id = await self._get_cart_restaurant_id(user_id)
        if existing_restaurant_id is not None and existing_restaurant_id != menu_item.restaurant_id:
            if not clear_existing:
                raise Duplicate(msg="購物車內已有其他餐廳的餐點，請先清空購物車或加上 clear_existing 參數")
            await self._session.execute(delete(Cart).where(Cart.user_id == user_id))

        existing_cart_item = await self._get_cart_item_by_menu(user_id, item.menu_item_id)
        if existing_cart_item is not None:
            stmt = (
                update(Cart)
                .values(quantity=existing_cart_item.quantity + item.quantity)
                .where(Cart.id == existing_cart_item.id)
            )
        else:
            stmt = (
                insert(Cart)
                .values(user_id=user_id, menu_item_id=item.menu_item_id, quantity=item.quantity)
            )
        await self._session.execute(stmt)

        response = await self.get_cart_response(user_id)
        response["message"] = "已加入購物車!"
        return response
