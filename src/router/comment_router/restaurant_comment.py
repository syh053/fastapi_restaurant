from typing import Annotated

from fastapi import APIRouter, Depends, Cookie

from src.service.front_service.comment.create_comment import CommentService
from src.tool.service_tool import get_service
from src.vm.comment.comment_vm import CommentCreateReqModel
from src.vm.response.response_vm import ResponseModel

RESTAURANT_COMMENT_ROUTER = APIRouter(
    prefix="/restaurant",
    tags=["餐廳評論"]
)
COMMENT_SERVICE = Annotated[CommentService, Depends(get_service(CommentService))]


@RESTAURANT_COMMENT_ROUTER.post("", response_model=ResponseModel)
async def comment_post(
        session_id: Annotated[str, Cookie],
        comment: CommentCreateReqModel,
        service: COMMENT_SERVICE
):
    return await service.create_comment(session_id=session_id, comment=comment)
