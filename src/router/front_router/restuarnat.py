from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependencies.auth import get_current_user
from src.service.front_service.restaurant import GetRestaurant
from src.tool.service_tool import get_service
from src.vm.end.restaurant_vm import EndRestaurantGetReqModel

RESTAURANT_ROUTER = APIRouter(
    prefix="/restaurant",
    tags=["前台-餐廳"],
    dependencies=[Depends(get_current_user)]
)

FRONT_RESTAURANT_SERVICE = Annotated[GetRestaurant, Depends(get_service(GetRestaurant))]


@RESTAURANT_ROUTER.get("/all", summary="餐聽列表")
async def get_restaurant(
        service: FRONT_RESTAURANT_SERVICE,
        query_params: Annotated[EndRestaurantGetReqModel, Query(description='查詢參數')],
):
    return await service.get_all_restaurant(params=query_params)


@RESTAURANT_ROUTER.get("/category", summary="取得餐廳類別列表")
async def get_restaurant_category(
        service: FRONT_RESTAURANT_SERVICE,
):
    return await service.get_category()
