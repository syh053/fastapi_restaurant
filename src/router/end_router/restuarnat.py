from typing import Annotated

from errors import Duplicate
from fastapi import APIRouter, Depends, HTTPException, Body, Query

from src.dependencies.auth import require_admin
from src.service.end_service.crud import CRUDRestaurant
from src.service.end_service.restaurant import GetRestaurant
from src.tool.servuce_tool import get_service
from src.vm.end_restaurant.restaurant_vm import EndRestaurantGetReqModel, EndRestaurantReqModel

RESTAURANT_ROUTER = APIRouter(
    prefix="/restaurant",
    tags=["後台-餐廳"],
    dependencies=[Depends(require_admin)]
)
END_RESTAURANT_SERVICE = Annotated[GetRestaurant, Depends(get_service(GetRestaurant))]
END_RESTAURANT_CRUD_SERVICE = Annotated[CRUDRestaurant, Depends(get_service(CRUDRestaurant))]


@RESTAURANT_ROUTER.get("/all", summary="餐聽列表")
async def get_restaurant(
        service: END_RESTAURANT_SERVICE,
        query_params: EndRestaurantGetReqModel = Depends()
):
    return await service.get_all_restaurant(params=query_params)


@RESTAURANT_ROUTER.post("", summary="新增餐廳")
async def add_restaurant(
        service: END_RESTAURANT_CRUD_SERVICE,
        restaurant: EndRestaurantReqModel
):
    await service.add_restaurant(restaurant=restaurant)


@RESTAURANT_ROUTER.put("", summary="編輯餐廳")
async def update_restaurant(
        service: END_RESTAURANT_CRUD_SERVICE,
        original_name: Annotated[str, Body(description='原來的餐廳名稱')],
        restaurant: EndRestaurantReqModel
):
    await service.update_restaurant(original_name=original_name ,restaurant=restaurant)


@RESTAURANT_ROUTER.delete("", summary="刪除餐廳")
async def delete_restaurant(
        service: END_RESTAURANT_CRUD_SERVICE,
        name_list: Annotated[list[str], Query(description='餐廳名稱')]
):
    print("list_name :", name_list)
    await service.delete_restaurant(restaurant_name_list=name_list)
