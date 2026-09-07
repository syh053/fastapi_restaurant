from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Cookie, Body

from src.dependencies.auth import get_current_user
from src.service.front_service.cart.create_cart_item import CartCreateService
from src.service.front_service.cart.drop_cart import CartDropService
from src.service.front_service.cart.get_cart import CartGetService
from src.service.front_service.cart.remove_cart_item import CartRemoveService
from src.service.front_service.cart.update_cart_item import CartUpdateService
from src.tool.service_tool import get_service
from src.vm.cart.cart_vm import CartItemReqModel, CartItemUpdateReqModel

CART_ROUTER = APIRouter(
    prefix="/cart",
    tags=["前台-購物車"],
    dependencies=[Depends(get_current_user)]
)

CURRENT_USER = Annotated[dict, Depends(get_current_user)]


@CART_ROUTER.get("", summary="查看購物車")
async def get_cart(
        service: Annotated[CartGetService, Depends(get_service(CartGetService))],
        user: CURRENT_USER
):
    return await service.get_cart_response(user_id=UUID(user["user_id"]))


@CART_ROUTER.post("", summary="加入購物車")
async def add_to_cart(
        service: Annotated[CartCreateService, Depends(get_service(CartCreateService))],
        user: CURRENT_USER,
        item: CartItemReqModel,
        clear_existing: Annotated[bool, Query(description="是否清空原有其他餐廳的購物車品項")] = False
):
    return await service.add_to_cart(user_id=UUID(user["user_id"]), item=item, clear_existing=clear_existing)


@CART_ROUTER.put("", summary="修改購物車品項數量")
async def update_cart_item(
        service: Annotated[CartUpdateService, Depends(get_service(CartUpdateService))],
        user: CURRENT_USER,
        item: Annotated[CartItemUpdateReqModel, Body()]
):
    return await service.update_quantity(
        user_id=UUID(user["user_id"]),
        item=item
    )

@CART_ROUTER.delete("", summary="移除購物車品項")
async def remove_cart_item(
        service: Annotated[CartRemoveService, Depends(get_service(CartRemoveService))],
        user: CURRENT_USER,
        cart_item_id: Annotated[UUID, Query(description="欲刪除的購物車項目 ID")]
):
    return await service.remove_from_cart(user_id=UUID(user["user_id"]), cart_item_id=cart_item_id)


@CART_ROUTER.delete("/cart_drop", summary="清空購物車")
async def clear_cart(
        service: Annotated[CartDropService, Depends(get_service(CartDropService))],
        user: CURRENT_USER
):
    return await service.clear_cart(user_id=UUID(user["user_id"]))
