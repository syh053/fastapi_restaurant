from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Cookie, Query

from src.dependencies.auth import get_current_user
from src.service.front_service.comment.create_comment import CommentCreateService
from src.service.front_service.comment.get_comment import CommentGetService
from src.tool.service_tool import get_service
from src.vm.comment.comment_vm import CommentCreateReqModel
from src.vm.response.response_vm import ResponseModel

RESTAURANT_COMMENT_ROUTER = APIRouter(
    prefix="/restaurant",
    tags=["餐廳評論"],
    dependencies=[Depends(get_current_user)]
)


@RESTAURANT_COMMENT_ROUTER.get("", summary="查看餐廳評論")
async def get_restaurant_comment(
        restaurant_id: Annotated[UUID, Query(description='餐廳 ID')],
        service: Annotated[CommentGetService, Depends(get_service(CommentGetService))]
):
    return await service.get_restaurant_comment(restaurant_id=restaurant_id)


@RESTAURANT_COMMENT_ROUTER.post("", summary="建立餐廳評論", response_model=ResponseModel)
async def comment_post(
        session_id: Annotated[str, Cookie],
        comment: CommentCreateReqModel,
        service: Annotated[CommentCreateService, Depends(get_service(CommentCreateService))]
):
    return await service.create_comment(session_id=session_id, comment=comment)
