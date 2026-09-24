from uuid import UUID

from custom_select.select import select
from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Order, OrderItem
from src.vm.order.order_vm import OrderRespModel, OrderItemRespModel


class OrderGetService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_order_list_response(self, user_id: UUID) -> dict:
        orders = await self._get_orders_by_user(user_id)
        data = [await self._to_order_resp(order) for order in orders]
        return {
            "code": 200,
            "message": "查詢訂單列表成功!",
            "data": data
        }

    async def get_order_detail_response(self, user_id: UUID, order_id: UUID) -> dict:
        order = await self._get_order_by_id(order_id)
        if order is None or order.user_id != user_id:
            raise Missing(msg="訂單不存在")

        return {
            "code": 200,
            "message": "查詢訂單成功!",
            "data": await self._to_order_resp(order)
        }

    async def _get_order_by_id(self, order_id: UUID) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_orders_by_user(self, user_id: UUID) -> list[Order]:
        stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def _get_order_items(self, order_id: UUID) -> list[OrderItem]:
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def _to_order_resp(self, order: Order) -> OrderRespModel:
        items = await self._get_order_items(order.id)
        return OrderRespModel(
            id=order.id,
            restaurant_id=order.restaurant_id,
            status=order.status,
            total_amount=order.total_amount,
            merchant_trade_no=order.merchant_trade_no,
            ecpay_trade_no=order.ecpay_trade_no,
            payment_date=order.payment_date,
            items=[OrderItemRespModel.model_validate(item) for item in items],
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
