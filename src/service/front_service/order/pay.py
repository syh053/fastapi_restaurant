from uuid import UUID

from database_errors.errors import Missing
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.front_service.order.get_order import OrderGetService
from src.tool import ecpay_tool


class OrderPayService(OrderGetService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def build_pay_form(self, user_id: UUID, order_id: UUID) -> dict:
        order = await self._get_order_by_id(order_id)
        if order is None or order.user_id != user_id:
            raise Missing(msg="訂單不存在")
        if order.status != "pending":
            raise Missing(msg="此訂單無法付款（狀態非待付款）")

        items = await self._get_order_items(order_id)
        fields = ecpay_tool.build_aio_checkout_params(order, items)

        return {"action_url": ecpay_tool.get_action_url(), "fields": fields}
