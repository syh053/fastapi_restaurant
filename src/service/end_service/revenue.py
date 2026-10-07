import uuid

from custom_select.select import select
from database_errors.errors import Missing
from sqlalchemy import Date, cast, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Order, Restaurant
from src.vm.end.revenue_vm import (
    DailyRevenueModel,
    RestaurantRevenueModel,
    RevenueGetReqModel,
    RevenueRespModel,
)

# 營業日以台灣時區計算
TIMEZONE = "Asia/Taipei"


class RevenueService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_revenue(self, owner_id: uuid.UUID, params: RevenueGetReqModel) -> RevenueRespModel:
        """
        取得業者名下餐廳的營業額(僅計算已付款訂單)

        :param owner_id: 業者 ID
        :param params: 日期區間與餐廳篩選條件
        :return: 總營業額、總訂單數、依日期統計與各餐廳小計
        """
        if params.restaurant_id:
            await self._check_restaurant_owned(owner_id, params.restaurant_id)

        pay_date = cast(func.timezone(TIMEZONE, Order.payment_date), Date)

        daily_stmt = (
            select(
                pay_date.label("date"),
                func.count(Order.id).label("order_count"),
                func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
            )
            .select_from(Order)
            .join(Restaurant, Restaurant.id == Order.restaurant_id)
            .where(Restaurant.owner_id == owner_id)
            .where(Order.status == "paid")
            .where_if(params.restaurant_id, lambda: Order.restaurant_id == params.restaurant_id)
            .where_if(params.start_date, lambda: pay_date >= params.start_date)
            .where_if(params.end_date, lambda: pay_date <= params.end_date)
            .group_by(pay_date)
            .order_by(pay_date)
        )
        restaurant_stmt = (
            select(
                Restaurant.id,
                Restaurant.name,
                func.count(Order.id).label("order_count"),
                func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
            )
            .select_from(Order)
            .join(Restaurant, Restaurant.id == Order.restaurant_id)
            .where(Restaurant.owner_id == owner_id)
            .where(Order.status == "paid")
            .where_if(params.restaurant_id, lambda: Order.restaurant_id == params.restaurant_id)
            .where_if(params.start_date, lambda: pay_date >= params.start_date)
            .where_if(params.end_date, lambda: pay_date <= params.end_date)
            .group_by(Restaurant.id, Restaurant.name)
            .order_by(Restaurant.name)
        )

        daily_rows = (await self._session.execute(daily_stmt)).all()
        restaurant_rows = (await self._session.execute(restaurant_stmt)).all()

        daily = [
            DailyRevenueModel(date=row.date, order_count=row.order_count, revenue=row.revenue)
            for row in daily_rows
        ]
        restaurants = [
            RestaurantRevenueModel(
                restaurant_id=row.id,
                restaurant_name=row.name,
                order_count=row.order_count,
                revenue=row.revenue,
            )
            for row in restaurant_rows
        ]

        return RevenueRespModel(
            total_revenue=sum(item.revenue for item in daily),
            total_orders=sum(item.order_count for item in daily),
            daily=daily,
            restaurants=restaurants,
        )

    async def _check_restaurant_owned(self, owner_id: uuid.UUID, restaurant_id: uuid.UUID) -> None:
        stmt = (
            select(Restaurant.id)
            .where(Restaurant.id == restaurant_id)
            .where(Restaurant.owner_id == owner_id)
        )
        if (await self._session.execute(stmt)).scalar_one_or_none() is None:
            raise Missing(msg="餐廳不存在")
