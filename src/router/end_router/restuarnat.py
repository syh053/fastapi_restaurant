import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Body, Query, File, UploadFile, Form

from src.dependencies.auth import require_admin
from src.service.end_service.crud import CRUDRestaurant
from src.service.end_service.restaurant import GetRestaurant
from src.tool.service_tool import get_service
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
        query_params: Annotated[EndRestaurantGetReqModel, Query(description='查詢參數')]
):
    return await service.get_all_restaurant(params=query_params)


@RESTAURANT_ROUTER.get("/category", summary="取得餐廳類別列表")
async def get_restaurant_category(
        service: END_RESTAURANT_SERVICE,
):
    return await service.get_category()


@RESTAURANT_ROUTER.post("", summary="新增餐廳")
async def add_restaurant(
        service: END_RESTAURANT_CRUD_SERVICE,
        name: str = Form(description='餐廳名稱'),
        tel: str | None = Form(default=None, description='餐廳電話'),
        opening_hours: int = Form(description='營業時長'),
        address: str = Form(description='餐廳地址'),
        description: str | None = Form(default=None, description='描述'),
        category_id: uuid.UUID | None = Form(default=None, examples=[None], description='餐廳分類'),
        image: Annotated[UploadFile | None, File(description='餐廳照片')] = None
):
    restaurant = EndRestaurantReqModel(
        name=name,
        tel=tel,
        openingHours=opening_hours,
        address=address,
        description=description,
        category_id=category_id
    )

    await service.add_restaurant(restaurant=restaurant, file=image)


@RESTAURANT_ROUTER.put("", summary="編輯餐廳")
async def update_restaurant(
        service: END_RESTAURANT_CRUD_SERVICE,
        original_name: Annotated[str, Body(description='原來的餐廳名稱')],
        name: str = Form(description='餐廳名稱'),
        tel: str | None = Form(default=None, description='餐廳電話'),
        opening_hours: int = Form(description='營業時長'),
        address: str = Form(description='餐廳地址'),
        description: str | None = Form(default=None, description='描述'),
        category_id: uuid.UUID | None = Form(default=None, examples=[None], description='餐廳分類'),
        image: Annotated[UploadFile | None, File(description='餐廳照片')] = None
):
    restaurant = EndRestaurantReqModel(
        name=name,
        tel=tel,
        openingHours=opening_hours,
        address=address,
        description=description,
        category_id=category_id
    )
    await service.update_restaurant(original_name=original_name, restaurant=restaurant, file=image)


@RESTAURANT_ROUTER.delete("", summary="刪除餐廳")
async def delete_restaurant(
        service: END_RESTAURANT_CRUD_SERVICE,
        name_list: Annotated[list[str], Query(description='餐廳名稱')]
):
    await service.delete_restaurant(restaurant_name_list=name_list)
