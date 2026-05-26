import bcrypt
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model.user import User
from src.vm.user.user_vm import UserGetReqModel, UserGetRespModel


class GetUser:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, user: UserGetReqModel) -> UserGetRespModel:
        stmt = select(User).select_from(User).where(User.name == user.name)
        result = await self._session.execute(stmt)
        db_user = result.scalars().one_or_none()

        if not db_user:
            raise HTTPException(status_code=400, detail="錯誤的使用者名稱或密碼")

        if bcrypt.checkpw(user.password.encode("utf-8"), db_user.password.encode("utf-8")):
            return UserGetRespModel(name=db_user.name, email=db_user.email)
        else:
            raise HTTPException(status_code=400, detail="錯誤的使用者名稱或密碼")
