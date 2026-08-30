from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.dependencies.auth import get_current_user
from src.service.front_service.menu import GetMenuService
from src.tool.service_tool import get_service

MENU_ROUTER = APIRouter(
    prefix="/menu",
    tags=["前台-菜單"],
    dependencies=[Depends(get_current_user)]
)

FRONT_MENU_SERVICE = Annotated[GetMenuService, Depends(get_service(GetMenuService))]


@MENU_ROUTER.get("", summary="查看餐廳菜單")
async def get_restaurant_menu(
        service: FRONT_MENU_SERVICE,
        restaurant_id: Annotated[UUID, Query(description='餐廳 ID')]
):
    return await service.get_restaurant_menu(restaurant_id=restaurant_id)
