from html import escape
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from src.dependencies.auth import get_current_user
from src.service.front_service.order.checkout import OrderCheckoutService
from src.service.front_service.order.get_order import OrderGetService
from src.service.front_service.order.pay import OrderPayService
from src.tool.service_tool import get_service

ORDER_ROUTER = APIRouter(
    prefix="/order",
    tags=["前台-訂單"],
    dependencies=[Depends(get_current_user)]
)

CURRENT_USER = Annotated[dict, Depends(get_current_user)]


@ORDER_ROUTER.post("", summary="購物車結帳，建立訂單")
async def checkout(
        service: Annotated[OrderCheckoutService, Depends(get_service(OrderCheckoutService))],
        user: CURRENT_USER
):
    return await service.checkout(user_id=UUID(user["user_id"]))


@ORDER_ROUTER.get("", summary="查詢我的訂單列表")
async def get_order_list(
        service: Annotated[OrderGetService, Depends(get_service(OrderGetService))],
        user: CURRENT_USER
):
    return await service.get_order_list_response(user_id=UUID(user["user_id"]))


@ORDER_ROUTER.get("/{order_id}", summary="查詢訂單明細")
async def get_order_detail(
        service: Annotated[OrderGetService, Depends(get_service(OrderGetService))],
        user: CURRENT_USER,
        order_id: UUID
):
    return await service.get_order_detail_response(user_id=UUID(user["user_id"]), order_id=order_id)


@ORDER_ROUTER.get("/{order_id}/pay", summary="前往綠界付款頁（自動送出表單導頁）")
async def pay_order(
        service: Annotated[OrderPayService, Depends(get_service(OrderPayService))],
        user: CURRENT_USER,
        order_id: UUID
):
    pay_form = await service.build_pay_form(user_id=UUID(user["user_id"]), order_id=order_id)

    inputs_html = "\n".join(
        f'<input type="hidden" name="{escape(str(key))}" value="{escape(str(value))}">'
        for key, value in pay_form["fields"].items()
    )
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head><meta charset="utf-8"><title>導向綠界付款頁...</title></head>
    <body onload="document.forms[0].submit()">
        <form method="POST" action="{pay_form['action_url']}">
            {inputs_html}
        </form>
        <p>正在導向付款頁面，請稍候...</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
