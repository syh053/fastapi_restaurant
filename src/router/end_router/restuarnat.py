from fastapi import APIRouter, Depends

from src.router.dependencies.auth import get_current_user, require_admin

RESTAURANT_ROUTER = APIRouter(
    prefix="/restaurant",
    tags=["後台-餐廳"],
    dependencies=[Depends(get_current_user), Depends(require_admin)]
)


@RESTAURANT_ROUTER.get("/all")
async def get_restaurant():
    return "這裡是後台餐廳 API"
