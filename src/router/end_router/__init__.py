from fastapi import APIRouter

from src.router.end_router.restuarnat import RESTAURANT_ROUTER
from src.router.end_router.user import END_USER_ROUTER

END_ROUTER = APIRouter(prefix="/end")

END_ROUTER.include_router(RESTAURANT_ROUTER)
END_ROUTER.include_router(END_USER_ROUTER)

