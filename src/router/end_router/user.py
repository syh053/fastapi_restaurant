from typing import Annotated

from fastapi import APIRouter, Depends, Query
from watchfiles import awatch

from src.dependencies.auth import require_admin
from src.service.end_service.user import UserCrud
from src.tool.service_tool import get_service
from src.vm.end.user_vm import EndUserGetReqModel

END_USER_ROUTER = APIRouter(
    prefix="/user",
    tags=["後台-管理使用者"],
    dependencies=[Depends(require_admin)]
)

END_USER_SERVICE = Annotated[UserCrud, Depends(get_service(UserCrud))]


@END_USER_ROUTER.get("/all", summary="使用者列表")
async def get_user(
        service: END_USER_SERVICE,
        query_params: Annotated[EndUserGetReqModel, Query(description='查詢參數')]
):
    return await service.get_users(params=query_params)
