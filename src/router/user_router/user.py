from typing import Annotated

from fastapi import APIRouter, Depends

from src.service.user.add_user import AddUser
from src.service.user.get_user import GetUser
from src.tool.tool import get_service
from src.vm.user.user_vm import UserAddReq, UserGetReqModel

USER_ROUTER = APIRouter(prefix="/user", tags=["使用者"])


@USER_ROUTER.post("/signup")
async def signup(
        data: UserAddReq,
        service: Annotated[AddUser, Depends(get_service(AddUser))]
):
    return await service.add_user(user=data)


@USER_ROUTER.post("/login")
async def login(
        service: Annotated[GetUser, Depends(get_service(GetUser))],
        data: UserGetReqModel,
):
    return await service.get_user(user=data)
