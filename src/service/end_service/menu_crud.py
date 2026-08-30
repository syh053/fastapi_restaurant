import uuid
from pathlib import Path

import aiofiles
from custom_select.select import select
from database_errors.errors import Duplicate, Missing

from fastapi import UploadFile, HTTPException
from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import MenuItem
from src.service.basic.basic_service import BasicService
from src.vm.menu.menu_vm import MenuReqModel, MenuRespModel

menu_path = Path(__file__).resolve().parents[3] / "uploads"
menu_path.mkdir(parents=True, exist_ok=True)


class CRUDMenuService(BasicService):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_menu(self, menu: MenuReqModel, file: UploadFile | None) -> dict:
        """
        新增餐點功能

        :param menu: 新增的餐點資訊
        :param file: 上傳的餐點圖片檔案，若無則為 None。
        :return: 回傳新增成功訊息與新增後的餐點資料（含 id、section 預設值、建立/更新時間）
        """
        # section 為 None 時略過，交由資料庫自己填入「未分類」
        add_data = menu.model_dump(exclude_none=True)

        # 檔案處理
        if file:
            file_name: str = f"/assets/{file.filename}"
            await self._save_file_to_folder(file=file)
            add_data["image"] = file_name

        existed_restaurant = await self._check_if_existed_restaurant(self._session, menu.restaurant_id)
        if not existed_restaurant:
            raise Missing(msg="餐廳不存在")

        duplicated = await self._check_if_duplicated_menu(menu.restaurant_id, menu.name)
        if duplicated:
            raise Duplicate(msg="此餐點已存在")

        stmt = insert(MenuItem).values(**add_data).returning(MenuItem)
        result = await self._session.execute(stmt)
        created = result.scalar_one()

        return {
            "code": 200,
            "message": "餐點新增成功!",
            "data": MenuRespModel.model_validate(created)
        }

    async def update_menu(self,
                          menu_item_id: uuid.UUID,
                          menu: MenuReqModel,
                          file: UploadFile | None
                          ) -> dict:
        """
        編輯餐點功能

        :param menu_item_id: 欲修改的餐點 ID
        :param menu: 欲修改的餐點內容
        :param file: 上傳的餐點圖片檔案，若無則為 None。
        :return: 回傳編輯成功訊息與編輯後的餐點資料
        """
        # 傳 None 的欄位不覆寫既有值
        update_data = menu.model_dump(exclude_none=True)

        # 檔案處理
        if file:
            file_name: str = f"/assets/{file.filename}"
            await self._save_file_to_folder(file=file)
            update_data["image"] = file_name

        existed = await self._check_if_existed_menu_item(self._session, menu_item_id)
        if not existed:
            raise Missing(msg="餐點不存在")

        stmt = (
            update(MenuItem)
            .values(**update_data)
            .where(MenuItem.id == menu_item_id)
            .returning(MenuItem)
        )
        result = await self._session.execute(stmt)
        updated = result.scalar_one()

        return {
            "code": 200,
            "message": "餐點編輯成功!",
            "data": MenuRespModel.model_validate(updated)
        }

    async def delete_menu(self, menu_item_id_list: list[uuid.UUID]) -> dict:
        """
        刪除餐點功能

        :param menu_item_id_list: 欲刪除的餐點 ID 清單
        :return: 回傳刪除成功訊息與已刪除的餐點資料清單
        """
        for menu_item_id in menu_item_id_list:
            existed = await self._check_if_existed_menu_item(self._session, menu_item_id)
            if not existed:
                raise Missing(msg=f"餐點 {menu_item_id} 不存在，取消所有刪除，請確認。")

        stmt = delete(MenuItem).where(MenuItem.id.in_(menu_item_id_list)).returning(MenuItem)
        result = await self._session.execute(stmt)
        deleted = result.scalars().all()

        return {
            "code": 200,
            "message": "餐點刪除成功!",
            "data": [MenuRespModel.model_validate(item) for item in deleted]
        }

    async def _check_if_duplicated_menu(self, restaurant_id: uuid.UUID, name: str) -> bool:
        """
        檢查同一間餐廳內是否已有同名餐點

        :param restaurant_id: 所屬餐廳 ID
        :param name: 餐點名稱
        :return: 確認餐點是否重複
        """
        stmt = (
            select(MenuItem.id)
            .select_from(MenuItem)
            .where(MenuItem.restaurant_id == restaurant_id)
            .where(MenuItem.name == name)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def _save_file_to_folder(file: UploadFile) -> None:
        file_location = menu_path / file.filename

        try:
            async with aiofiles.open(file_location, mode="wb") as f:
                while content := await file.read(1024 * 4024):
                    await f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"檔案寫入失敗: {str(e)}")
        finally:
            await file.close()
