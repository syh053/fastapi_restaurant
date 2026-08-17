import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import User
from dependencies.auth import get_current_user
from vm.user.user_info_vm import UserInfoUpdateReqModel

FILE_PATH = Path(__file__).resolve().parents[3] / "uploads"
FILE_PATH.mkdir(parents=True, exist_ok=True)


class UpdateUserInfoService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def update_user_info(self, session_id: str, user_info_data: UserInfoUpdateReqModel, ):
        """
        變更使用者資訊

        :param: 傳入欲修改的資料內容，請至 UserInfoUpdateReqModel 查看詳細內容
        :return: 無回傳直
        """
        # 取得目前使用者 ID
        user_info = await get_current_user(session_id)
        current_user_id = user_info["user_id"]

        user_info_data_dict = user_info_data.model_dump(exclude_none=True)

        stmt = (
            update(User)
            .values(**user_info_data_dict)
            .where(User.id == current_user_id)
        )

        await self._session.execute(stmt)

        return {
            "code": 200,
            "message": "資料修改成功!"
        }

    async def update_user_image(self, session_id: str, file: UploadFile | None = None):
        # 取得目前使用者 ID
        user_info = await get_current_user(session_id)
        current_user_id = user_info["user_id"]

        # 檔案處理
        if file:
            file_name = await self._save_file_to_folder(file=file)
            file_name = f"/assets/{file_name}"

            stmt = (
                update(User)
                .values(image=file_name)
                .where(User.id == current_user_id)
            )

            await self._session.execute(stmt)

            return {
                "code": 200,
                "message": "大頭照更新成功!"
            }
        else:
            raise HTTPException(status_code=400, detail="請選擇圖片")

    @staticmethod
    async def _save_file_to_folder(file: UploadFile) -> str:
        filename = f'{uuid.uuid4()}_{file.filename}'

        file_location = FILE_PATH / filename

        try:
            async with aiofiles.open(file_location, mode="wb") as f:
                while content := await file.read(1024 * 4024):
                    await f.write(content)

                return filename
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"檔案寫入失敗: {str(e)}")
        finally:
            await file.close()
