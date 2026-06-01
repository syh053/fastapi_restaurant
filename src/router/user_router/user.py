from typing import Annotated

from errors import Missing
from fastapi import APIRouter, Depends, Response, HTTPException

from src.service.user.add_user import AddUser
from src.service.user.get_user import GetUser
from src.tool.servuce_tool import get_service
from src.vm.user.user_vm import UserAddReq, UserGetReqModel

USER_ROUTER = APIRouter(prefix="/user", tags=["使用者"])
USER_SERVICE = Annotated[GetUser, Depends(get_service(GetUser))]


@USER_ROUTER.post("/signup")
async def signup(
        data: UserAddReq,
        service: Annotated[AddUser, Depends(get_service(AddUser))]
):
    return await service.add_user(user=data)


@USER_ROUTER.post("/login")
async def login(
        service: USER_SERVICE,
        data: UserGetReqModel,
        response: Response
):
    try:
        await service.login(user=data, response=response)
    except Missing as e:
        raise HTTPException(status_code=400, detail=e.msg)


@USER_ROUTER.post("/logout")
async def logout(
        service: USER_SERVICE,
        response: Response
):
    await service.logout(response=response)
