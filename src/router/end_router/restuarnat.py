from fastapi import APIRouter

RESTAURANT_ROUTER = APIRouter(prefix="/restaurant", tags=["後台-餐廳"])


@RESTAURANT_ROUTER.get("/all")
async def get_restaurant():
    return "取得多個餐廳 API"