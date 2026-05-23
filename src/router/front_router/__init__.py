from fastapi import APIRouter

from src.router.front_router.restuarnat import RESTAURANT_ROUTER

FRONT_ROUTER = APIRouter(prefix="/front")

FRONT_ROUTER.include_router(RESTAURANT_ROUTER)
