from fastapi import APIRouter

from src.router.comment_router.restaurant_comment import RESTAURANT_COMMENT_ROUTER

CENTER_COMMENT_ROUTER = APIRouter(prefix="/comment")

CENTER_COMMENT_ROUTER.include_router(RESTAURANT_COMMENT_ROUTER)
