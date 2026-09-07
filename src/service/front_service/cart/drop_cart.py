from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Cart
from src.service.front_service.cart.get_cart import CartGetService
from src.vm.cart.cart_vm import CartRespModel


class CartDropService(CartGetService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def clear_cart(self, user_id: UUID) -> dict:
        """
        清空購物車

        :param user_id: 使用者 ID
        :return: 回傳清空成功訊息與空的購物車內容
        """
        await self._session.execute(delete(Cart).where(Cart.user_id == user_id))

        return {
            "code": 200,
            "message": "購物車已清空!",
            "data": CartRespModel(items=[], total=0)
        }
