import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependencies.auth import require_owner
from src.service.end_service.revenue import RevenueService
from src.tool.service_tool import get_service
from src.vm.end.revenue_vm import RevenueGetReqModel, RevenueRespModel

REVENUE_ROUTER = APIRouter(
    prefix="/revenue",
    tags=["後台-營業額"],
)

REVENUE_SERVICE = Annotated[RevenueService, Depends(get_service(RevenueService))]
CURRENT_OWNER = Annotated[dict, Depends(require_owner)]


@REVENUE_ROUTER.get("", summary="業者營業額(僅業者可查看自己名下餐廳)", response_model=RevenueRespModel)
async def get_revenue(
        service: REVENUE_SERVICE,
        owner: CURRENT_OWNER,
        query_params: Annotated[RevenueGetReqModel, Query(description='查詢參數')]
):
    return await service.get_revenue(owner_id=uuid.UUID(owner["user_id"]), params=query_params)
