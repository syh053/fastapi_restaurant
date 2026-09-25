from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from src.service.payment.ecpay_notify import EcpayNotifyService
from src.tool.ecpay_tool import parse_notify_form_body
from src.tool.service_tool import get_service

ECPAY_ROUTER = APIRouter(prefix="/ecpay", tags=["金流-綠界"])


@ECPAY_ROUTER.post("/notify", summary="綠界 Server 端付款結果通知（由綠界主機呼叫，不需登入）")
async def ecpay_notify(
        request: Request,
        service: EcpayNotifyService = Depends(get_service(EcpayNotifyService))
):
    body = await request.body()
    form_data = parse_notify_form_body(body)
    result = await service.handle_notify(form_data)
    return PlainTextResponse(content=result)
