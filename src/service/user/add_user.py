import bcrypt
from fastapi import HTTPException
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.model.user import User
from src.vm.user.user_vm import UserAddReq


class AddUser:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_user(self, user: UserAddReq) -> UserAddReq:
        if (not user.name) or (not user.email) or (not user.password) or (not user.confirm_password):
            raise HTTPException(status_code=400, detail="欄位填寫不完整")
        elif user.password != user.confirm_password:
            raise HTTPException(status_code=400, detail="密碼輸入不一致")

        new_user = (
            user.model_copy(update={"password": self._get_hashed_password(user.password)})
            .model_dump(exclude={"confirm_password"})
        )

        stmt = insert(User).values(new_user)
        await self._session.execute(stmt)
        await self._session.commit()

        return user

    @staticmethod
    def _get_hashed_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), salt=bcrypt.gensalt()).decode("utf-8")
