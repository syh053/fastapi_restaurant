from fastapi import APIRouter

from src.router.comment_router import CENTER_COMMENT_ROUTER
from src.router.end_router import END_ROUTER
from src.router.front_router import FRONT_ROUTER
from src.router.user_router.user import USER_ROUTER

TOTAL_ROUTER = APIRouter()

TOTAL_ROUTER.include_router(FRONT_ROUTER)
TOTAL_ROUTER.include_router(END_ROUTER)
TOTAL_ROUTER.include_router(USER_ROUTER)
TOTAL_ROUTER.include_router(CENTER_COMMENT_ROUTER)
