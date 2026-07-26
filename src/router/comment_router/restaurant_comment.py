from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Cookie, Query
from fastapi.openapi.models import Example

from src.dependencies.auth import get_current_user, require_admin
from src.service.front_service.comment.create_comment import CommentCreateService
from src.service.front_service.comment.delete_comment import CommentDeleteService
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
async def create_restaurant_comment(
        session_id: Annotated[str, Cookie],
        comment: CommentCreateReqModel,
        service: Annotated[CommentCreateService, Depends(get_service(CommentCreateService))]
):
    return await service.create_comment(session_id=session_id, comment=comment)


@RESTAURANT_COMMENT_ROUTER.delete("", summary="刪除餐廳評論", dependencies=[Depends(require_admin)])
async def delete_restaurant_comment(
        restaurant_id: Annotated[
            UUID,
            Query(
                openapi_examples={
                    "example_1": Example(
                        summary="正確的範例",
                        value={"restaurant_id": "d4b4bcf9-6be4-4d06-8f3e-3310aa918ba2"}
                    ),
                    "example_2": Example(
                        summary="錯誤的範例",
                        value={"restaurant_id": "林聰明滷肉飯"}
                    )
                },
                description='餐廳 ID'
            )
        ],
        comment_id: Annotated[
            UUID,
            Query(
                openapi_examples={
                    "example_1": Example(
                        summary="正確的範例",
                        value={"comment_id": "04a01d30-10d6-433a-a66e-a5a3a33815cf"}
                    ),
                    "example_2": Example(
                        summary="錯誤的範例",
                        value={"comment_id": "不好吃"}
                    )
                }, description='評論 ID'
            )
        ],
        service: Annotated[CommentDeleteService, Depends(get_service(CommentDeleteService))]
):
    return await service.delete_comment(restaurant_id=restaurant_id, comment_id=comment_id)
