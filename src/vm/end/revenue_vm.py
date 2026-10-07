import uuid
from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class RevenueGetReqModel(BaseModel):
    start_date: Annotated[date | None, Field(description='起始日期(含)')] = None
    end_date: Annotated[date | None, Field(description='結束日期(含)')] = None
    restaurant_id: Annotated[uuid.UUID | None, Field(description='指定餐廳 ID，未填則統計名下所有餐廳')] = None


class DailyRevenueModel(BaseModel):
    date: Annotated[date, Field(description='日期')]
    order_count: Annotated[int, Field(description='訂單數')]
    revenue: Annotated[int, Field(description='營業額(新台幣)')]


class RestaurantRevenueModel(BaseModel):
    restaurant_id: Annotated[uuid.UUID, Field(description='餐廳 ID')]
    restaurant_name: Annotated[str, Field(description='餐廳名稱')]
    order_count: Annotated[int, Field(description='訂單數')]
    revenue: Annotated[int, Field(description='營業額(新台幣)')]


class RevenueRespModel(BaseModel):
    total_revenue: Annotated[int, Field(description='總營業額(新台幣)')]
    total_orders: Annotated[int, Field(description='總訂單數')]
    daily: Annotated[list[DailyRevenueModel], Field(description='依日期統計')]
    restaurants: Annotated[list[RestaurantRevenueModel], Field(description='各餐廳小計')]
