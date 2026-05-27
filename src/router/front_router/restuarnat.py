from fastapi import APIRouter, Depends

from src.router.dependencies.auth import get_current_user, require_admin

RESTAURANT_ROUTER = APIRouter(
    prefix="/restaurant",
    tags=["前台-餐廳"],
    dependencies=[Depends(get_current_user)]
)


@RESTAURANT_ROUTER.get("/all")
async def get_restaurant():
    return "這裡是前台餐廳 API"
