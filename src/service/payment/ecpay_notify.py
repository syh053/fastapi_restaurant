from datetime import datetime

from custom_select.select import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Order
from src.tool.ecpay_tool import verify_notify_check_mac_value


class EcpayNotifyService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def handle_notify(self, form_data: dict) -> str:
        """
        處理綠界 Server 端 Notify 回呼，回傳值需依綠界規範為純文字 "1|OK" 或失敗訊息
        """
        if not verify_notify_check_mac_value(form_data):
            return "0|CheckMacValue Error"

        order = await self._get_order_by_merchant_trade_no(form_data.get("MerchantTradeNo"))
        if order is None:
            return "0|Order Not Found"

        if order.status == "paid":
            return "1|OK"

        if form_data.get("RtnCode") == "1":
            payment_date = self._parse_payment_date(form_data.get("PaymentDate"))
            stmt = (
                update(Order)
                .values(
                    status="paid",
                    ecpay_trade_no=form_data.get("TradeNo"),
                    payment_date=payment_date,
                )
                .where(Order.id == order.id)
            )
        else:
            stmt = update(Order).values(status="failed").where(Order.id == order.id)

        await self._session.execute(stmt)
        return "1|OK"

    async def _get_order_by_merchant_trade_no(self, merchant_trade_no: str | None) -> Order | None:
        if not merchant_trade_no:
            return None
        stmt = select(Order).where(Order.merchant_trade_no == merchant_trade_no)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def _parse_payment_date(payment_date_str: str | None) -> datetime | None:
        if not payment_date_str:
            return None
        return datetime.strptime(payment_date_str, "%Y/%m/%d %H:%M:%S")
