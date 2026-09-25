import uuid
from uuid import UUID

from database_errors.errors import Missing
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Order
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

        # 每次開啟付款頁都重新產生一組編號，避免重新整理時對綠界送出重複的編號
        merchant_trade_no = uuid.uuid4().hex[:20]
        stmt = (
            update(Order)
            .values(merchant_trade_no=merchant_trade_no)
            .where(Order.id == order_id)
        )
        await self._session.execute(stmt)
        # 上面的 ORM UPDATE 會讓 order 物件的 merchant_trade_no 變成過期(expired)，
        # 若直接讀 order.merchant_trade_no 會觸發同步 lazy-load 而丟出 MissingGreenlet，故用本地變數重新賦值
        order.merchant_trade_no = merchant_trade_no

        items = await self._get_order_items(order_id)
        fields = ecpay_tool.build_aio_checkout_params(order, items)

        return {"action_url": ecpay_tool.get_action_url(), "fields": fields}
