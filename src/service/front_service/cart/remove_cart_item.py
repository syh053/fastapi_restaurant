from uuid import UUID

from database_errors.errors import Missing
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Cart
from src.service.front_service.cart.get_cart import CartGetService


class CartRemoveService(CartGetService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def remove_from_cart(self, user_id: UUID, cart_item_id: UUID) -> dict:
        """
        移除購物車品項

        :param user_id: 使用者 ID
        :param cart_item_id: 購物車品項 ID
        :return: 回傳移除成功訊息與最新購物車內容
        """
        existing = await self._get_cart_item_by_id(user_id, cart_item_id)
        if existing is None:
            raise Missing(msg="購物車品項不存在")

        await self._session.execute(delete(Cart).where(Cart.id == cart_item_id))

        response = await self.get_cart_response(user_id)
        response["message"] = "已從購物車移除!"
        return response
