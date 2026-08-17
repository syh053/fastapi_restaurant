from typing import Annotated

from fastapi import APIRouter, Depends, Response, Cookie, Query, Form, UploadFile, File, Body

from src.dependencies.auth import get_current_user
from src.service.user.update_user_info import UpdateUserInfoService
from src.service.user.add_user import AddUser
from src.service.user.get_user import GetUser
from src.service.user.user_info import GetUserInfoService
from src.tool.service_tool import get_service
from src.vm.user.user_vm import UserAddReq, UserGetReqModel
from src.vm.user.user_info_vm import UserInfoUpdateReqModel

USER_ROUTER = APIRouter(prefix="/user", tags=["使用者"])
USER_SERVICE = Annotated[GetUser, Depends(get_service(GetUser))]


@USER_ROUTER.get("/info", dependencies=[Depends(get_current_user)], summary="取得使用者資訊")
async def get_user_info(
        session_id: Annotated[str, Cookie()],
        service: Annotated[GetUserInfoService, Depends(get_service(GetUserInfoService))],
):
    return await service.get_user_info(session_id=session_id)


@USER_ROUTER.put("/info", summary="修改使用者資訊")
async def update_user_info(
        session_id: Annotated[str, Cookie()],
        service: Annotated[UpdateUserInfoService, Depends(get_service(UpdateUserInfoService))],
        user_info_data: Annotated[UserInfoUpdateReqModel, Body()]
):
    return await service.update_user_info(session_id=session_id, user_info_data=user_info_data)


@USER_ROUTER.put("/info/img", summary="修改使用者大頭貼")
async def update_user_info(
        session_id: Annotated[str, Cookie()],
        service: Annotated[UpdateUserInfoService, Depends(get_service(UpdateUserInfoService))],
        image: Annotated[UploadFile | None, File(description="使用者大頭貼")] = None,
):
    return await service.update_user_image(session_id=session_id, file=image)


@USER_ROUTER.get("/check_name_existed", summary="檢查使用者名稱是否存在")
async def check_user_existed(
        name: Annotated[str, Query(description="使用者名稱")],
        service: USER_SERVICE
):
    await service.check_user_existed(name=name)


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
    return await service.login(user=data, response=response)


@USER_ROUTER.post("/logout", summary="使用者登出")
async def logout(
        service: USER_SERVICE,
        response: Response,
        session_id: str | None = Cookie(default=None),
):
    await service.logout(response=response, session_id=session_id)
