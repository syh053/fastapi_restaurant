from typing import Annotated

from fastapi import APIRouter, Depends, Response, Cookie, Query

from src.service.user.add_user import AddUser
from src.service.user.get_user import GetUser
from src.tool.service_tool import get_service
from src.vm.user.user_vm import UserAddReq, UserGetReqModel

USER_ROUTER = APIRouter(prefix="/user", tags=["使用者"])
USER_SERVICE = Annotated[GetUser, Depends(get_service(GetUser))]


@USER_ROUTER.get("/check_name_existed", summary="檢查使用者名稱是否存在")
async def check_user_existed(
        name: Annotated[str, Query(description="使用者名稱")],
        service: USER_SERVICE
):
    return await service.check_user_existed(name=name)


@USER_ROUTER.get("/check_email_existed", summary="檢查信箱是否存在")
async def check_user_existed(
        email: Annotated[str, Query(description="使用者信箱")],
        service: USER_SERVICE
):
    return await service.check_email_existed(email=email)


@USER_ROUTER.post("/signup", summary="使用者註冊")
async def signup(
        data: UserAddReq,
        service: Annotated[AddUser, Depends(get_service(AddUser))]
):
    return await service.add_user(user=data)


@USER_ROUTER.post("/login", summary="使用者登入")
async def login(
        service: USER_SERVICE,
        data: UserGetReqModel,
        response: Response
):
    await service.login(user=data, response=response)


@USER_ROUTER.post("/logout", summary="使用者登出")
async def logout(
        service: USER_SERVICE,
        response: Response,
        session_id: str | None = Cookie(default=None),
):
    await service.logout(response=response, session_id=session_id)
