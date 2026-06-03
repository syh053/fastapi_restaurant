from typing import Annotated

from errors import Duplicate
from fastapi import APIRouter, Depends, HTTPException

from src.dependencies.auth import get_current_user, require_admin
from src.service.end_service.crud import CRUDRestaurant
from src.service.end_service.restaurant import GetRestaurant
from src.tool.servuce_tool import get_service
from src.vm.end_restaurant.restaurant_vm import EndRestaurantGetReqModel, EndRestaurantAddReqModel

RESTAURANT_ROUTER = APIRouter(
    prefix="/restaurant",
    tags=["後台-餐廳"],
    dependencies=[Depends(require_admin)]
)
END_RESTAURANT_SERVICE = Annotated[GetRestaurant, Depends(get_service(GetRestaurant))]
END_RESTAURANT_CRUD_SERVICE = Annotated[CRUDRestaurant, Depends(get_service(CRUDRestaurant))]


@RESTAURANT_ROUTER.get("/all")
async def get_restaurant(
        service: END_RESTAURANT_SERVICE,
        query_params: EndRestaurantGetReqModel = Depends()
):
    return await service.get_all_restaurant(params=query_params)

@RESTAURANT_ROUTER.post("")
async def add_restaurant(
        service: END_RESTAURANT_CRUD_SERVICE,
        restaurant: EndRestaurantAddReqModel
):
    try:
        await service.add_restaurant(restaurant=restaurant)
    except Duplicate as e:
        raise HTTPException(status_code=404, detail=e.msg)
