import uuid
from uuid import UUID

from database_errors.errors import Missing
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Cart, Order, OrderItem
from src.service.front_service.cart.get_cart import CartGetService
from src.vm.order.order_vm import CheckoutRespModel, OrderItemRespModel, OrderRespModel


class OrderCheckoutService(CartGetService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def checkout(self, user_id: UUID) -> dict:
        cart_items, total = await self.get_cart(user_id)
        if not cart_items:
            raise Missing(msg="購物車是空的，無法結帳")

        restaurant_id = cart_items[0].restaurant_id
        merchant_trade_no = uuid.uuid4().hex[:20]

        order_stmt = (
            insert(Order)
            .values(
                user_id=user_id,
                restaurant_id=restaurant_id,
                total_amount=total,
                merchant_trade_no=merchant_trade_no,
            )
            .returning(Order.id, Order.status, Order.created_at, Order.updated_at)
        )
        order_result = await self._session.execute(order_stmt)
        order_row = order_result.one()

        item_values = [
            {
                "order_id": order_row.id,
                "menu_item_id": item.menu_item_id,
                "name": item.name,
                "unit_price": item.price,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
            }
            for item in cart_items
        ]
        item_stmt = (
            insert(OrderItem)
            .values(item_values)
            .returning(
                OrderItem.id, OrderItem.menu_item_id, OrderItem.name,
                OrderItem.unit_price, OrderItem.quantity, OrderItem.subtotal,
            ) # 成功建立資料後，設定 returning，可以回傳建立成功的資料
        )
        item_result = await self._session.execute(item_stmt)
        item_rows = item_result.all()

        await self._session.execute(delete(Cart).where(Cart.user_id == user_id))

        order_resp = OrderRespModel(
            id=order_row.id,
            restaurant_id=restaurant_id,
            status=order_row.status,
            total_amount=total,
            merchant_trade_no=merchant_trade_no,
            ecpay_trade_no=None,
            payment_date=None,
            items=[OrderItemRespModel(**row._mapping) for row in item_rows],
            created_at=order_row.created_at,
            updated_at=order_row.updated_at,
        )

        return {
            "code": 200,
            "message": "訂單已建立，請前往付款!",
            "data": CheckoutRespModel(order=order_resp, pay_url=f"/front/order/{order_row.id}/pay"),
        }
