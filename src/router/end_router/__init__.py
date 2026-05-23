from fastapi import APIRouter

from src.router.end_router.restuarnat import RESTAURANT_ROUTER

END_ROUTER = APIRouter(prefix="/end")

END_ROUTER.include_router(RESTAURANT_ROUTER)

