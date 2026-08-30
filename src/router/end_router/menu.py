import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, File, UploadFile, Form

from src.dependencies.auth import require_admin
from src.service.end_service.menu import GetMenuService
from src.service.end_service.menu_crud import CRUDMenuService
from src.tool.service_tool import get_service
from src.vm.menu.menu_vm import MenuGetReqModel, MenuReqModel
from src.vm.response.response_vm import ResponseModel

MENU_ROUTER = APIRouter(
    prefix="/menu",
    tags=["後台-菜單"],
    dependencies=[Depends(require_admin)]
)
END_MENU_SERVICE = Annotated[GetMenuService, Depends(get_service(GetMenuService))]
END_MENU_CRUD_SERVICE = Annotated[CRUDMenuService, Depends(get_service(CRUDMenuService))]


@MENU_ROUTER.get("/all", summary="菜單列表")
async def get_all_menu(
        service: END_MENU_SERVICE,
        query_params: Annotated[MenuGetReqModel, Query(description='查詢參數')]
):
    return await service.get_all_menu(params=query_params)


@MENU_ROUTER.post("", summary="新增餐點", response_model=ResponseModel)
async def add_menu(
        service: END_MENU_CRUD_SERVICE,
        restaurant_id: uuid.UUID = Form(description='所屬餐廳 ID'),
        name: str = Form(description='餐點名稱'),
        price: int = Form(description='價格（新台幣，整數）'),
        section: str | None = Form(default=None, description='分區（例：前菜／主餐／飲料）'),
        section_order: int | None = Form(default=None, description='分區排序（數字越小越前面）'),
        description: str | None = Form(default=None, description='餐點描述'),
        image: Annotated[UploadFile | None, File(description='餐點照片')] = None
):
    menu = MenuReqModel(
        restaurant_id=restaurant_id,
        name=name,
        price=price,
        section=section,
        section_order=section_order,
        description=description
    )
    return await service.add_menu(menu=menu, file=image)


@MENU_ROUTER.put("", summary="編輯餐點")
async def update_menu(
        service: END_MENU_CRUD_SERVICE,
        menu_item_id: uuid.UUID = Form(description='欲編輯的餐點 ID'),
        restaurant_id: uuid.UUID = Form(description='所屬餐廳 ID'),
        name: str = Form(description='餐點名稱'),
        price: int = Form(description='價格（新台幣，整數）'),
        section: str | None = Form(default=None, description='分區（例：前菜／主餐／飲料）'),
        section_order: int | None = Form(default=None, description='分區排序（數字越小越前面）'),
        description: str | None = Form(default=None, description='餐點描述'),
        image: Annotated[UploadFile | None, File(description='餐點照片')] = None
):
    menu = MenuReqModel(
        restaurant_id=restaurant_id,
        name=name,
        price=price,
        section=section,
        section_order=section_order,
        description=description
    )
    return await service.update_menu(menu_item_id=menu_item_id, menu=menu, file=image)


@MENU_ROUTER.delete("", summary="刪除餐點")
async def delete_menu(
        service: END_MENU_CRUD_SERVICE,
        id_list: Annotated[list[uuid.UUID], Query(description='欲刪除的餐點 ID')]
):
    return await service.delete_menu(menu_item_id_list=id_list)
