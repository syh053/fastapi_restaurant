from pathlib import Path

import aiofiles
from custom_select.select import select
from errors import Duplicate, Missing
from fastapi import UploadFile, HTTPException
from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Restaurant
from src.vm.end_restaurant.restaurant_vm import EndRestaurantReqModel

restaurant_path = Path(__file__).resolve().parents[3] / "uploads"
restaurant_path.mkdir(parents=True, exist_ok=True)


class CRUDRestaurant:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_restaurant(self, restaurant: EndRestaurantReqModel, file: UploadFile | None) -> None:
        """
        新增餐廳功能

        :param restaurant: 新增的餐廳資訊
        :param file: 上傳的餐廳圖片檔案，若無則為 None。
        :return: 無
        """

        # 檔案處理
        file_name: str = f"/assets/{file.filename}"
        await self._save_file_to_folder(file=file)

        existed = await self._check_if_existed_restaurant(restaurant.name)

        if not existed:
            stmt = insert(Restaurant).values(
                **restaurant.model_dump(),
                image=file_name
            )

            await self._session.execute(stmt)
            await self._session.commit()
        else:
            raise Duplicate(msg='此餐廳已存在')

    async def update_restaurant(self,
                                original_name: str,
                                restaurant: EndRestaurantReqModel,
                                file: UploadFile | None
                                ) -> None:
        """

        :param original_name: 原來的餐廳名稱
        :param restaurant: 欲修改的餐廳內容
        :param file: 上傳的餐廳圖片檔案，若無則為 None。
        :return: 無
        """

        update_data = restaurant.model_dump()

        # 檔案處理
        if file:
            file_name: str = f"/assets/{file.filename}"
            await self._save_file_to_folder(file=file)
            update_data["image"] = file_name

        existed = await self._check_if_existed_restaurant(original_name)

        if existed:
            stmt = (
                update(Restaurant)
                .values(**update_data)
                .where(Restaurant.name == original_name)
            )

            await self._session.execute(stmt)
            await self._session.commit()
        else:
            raise Missing(msg="餐廳不存在")

    async def delete_restaurant(self, restaurant_name_list: list[str]) -> None:
        """

        :param restaurant_name_list: 欲刪除的餐廳名稱
        :type restaurant_name_list: list[str]
        :return: 無
        """
        for name in restaurant_name_list:
            existed = await self._check_if_existed_restaurant(name)
            if not existed:
                raise Missing(msg=f"餐廳 {name} 不存在，取消所有刪除，請確認。")

        stmt = delete(Restaurant).where(Restaurant.name.in_(restaurant_name_list))

        await self._session.execute(stmt)
        await self._session.commit()

    async def _check_if_existed_restaurant(self, name: str) -> bool:
        stmt = (
            select(Restaurant.name)
            .select_from(Restaurant)
            .where(Restaurant.name == name)
        )

        result = await self._session.execute(stmt)

        if result.scalar_one_or_none():
            return True
        else:
            return False

    async def _save_file_to_folder(self, file: UploadFile) -> None:
        file_location = restaurant_path / file.filename

        try:
            async with aiofiles.open(file_location, mode="wb") as f:
                while content := await file.read(1024 * 4024):
                    await f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"檔案寫入失敗: {str(e)}")
        finally:
            await file.close()
