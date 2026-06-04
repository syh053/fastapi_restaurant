from typing import Annotated

from fastapi import Query, Body
from pydantic import BaseModel, Field, ConfigDict


class EndRestaurantGetReqModel(BaseModel):
    name: Annotated[str | None, Query(description='餐廳名稱')] = None
    tel: Annotated[str | None, Query(description='餐廳電話')] = None
    openingHours: Annotated[int | None, Query(description='餐廳營業時長')] = None
    address: Annotated[str | None, Query(description='餐廳營業時長')] = None
    description: Annotated[str | None, Query(description='備註')] = None
    current_page: Annotated[int, Query(description='目前分頁')] = 0
    page_size: Annotated[int, Query(description='分頁大小')] = 10


class EndRestaurantRespModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Annotated[str, Field(description='餐廳名稱')]
    tel: Annotated[str, Field(description='餐廳電話')]
    openingHours: Annotated[int, Field(description='餐廳營業時長')]
    address: Annotated[str, Field(description='餐廳營業時長')]
    description: Annotated[str | None, Field(default=None, description='備註')]


class EndRestaurantReqModel(BaseModel):
    name: Annotated[str, Body(description='餐廳名稱')]
    tel: Annotated[str | None, Body(default=None, description='餐廳電話')]
    openingHours: Annotated[int, Body(description='餐廳營業時長')]
    address: Annotated[str, Body(description='餐廳營業時長')]
    description: Annotated[str | None, Body(default=None, description='備註')]
