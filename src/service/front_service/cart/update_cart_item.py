from uuid import UUID

from database_errors.errors import Missing
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Cart
from src.service.front_service.cart.get_cart import CartGetService


class CartUpdateService(CartGetService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def update_quantity(self, user_id: UUID, cart_item_id: UUID, quantity: int) -> dict:
        """
        修改購物車品項數量

        :param user_id: 使用者 ID
        :param cart_item_id: 購物車品項 ID
        :param quantity: 欲修改成的數量
        :return: 回傳修改成功訊息與最新購物車內容
        """
        existing = await self._get_cart_item_by_id(user_id, cart_item_id)
        if existing is None:
            raise Missing(msg="購物車品項不存在")

        stmt = update(Cart).values(quantity=quantity).where(Cart.id == cart_item_id)
        await self._session.execute(stmt)

        response = await self.get_cart_response(user_id)
        response["message"] = "購物車數量已更新!"
        return response
