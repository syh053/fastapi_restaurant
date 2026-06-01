from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import get_current_user, require_admin
from src.service.end_service.restaurant import GetRestaurant
from src.tool.servuce_tool import get_service
from src.vm.end_restaurant.restaurant_vm import EndRestaurantGetReqModel

RESTAURANT_ROUTER = APIRouter(
    prefix="/restaurant",
    tags=["後台-餐廳"],
    dependencies=[Depends(require_admin)]
)
END_RESTAURANT_SERVICE = Annotated[GetRestaurant, Depends(get_service(GetRestaurant))]


@RESTAURANT_ROUTER.get("/all")
async def get_restaurant(
        service: END_RESTAURANT_SERVICE,
        query_params: EndRestaurantGetReqModel = Depends()
):
    print("query_params :", query_params)
    return await service.get_all_restaurant(params=query_params)
