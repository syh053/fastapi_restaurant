from typing import TypeVar, Type
from uuid import uuid4

from errors import Missing
from fastapi import HTTPException
from fastapi import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model.user import User
from src.dependencies.auth import check_password
from src.tool.redis_client import create_session, delete_session
from src.vm.user.user_vm import UserGetReqModel, UserGetRespModel

T = TypeVar("T")


class GetUser:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def login(
            self,
            user: UserGetReqModel,
            response: Response
    ) -> None:
        """
        驗證登入

        :param user: 參照 UserGetReqModel
        :param response: 設定 Cookie
        :return: 無回傳值
        """
        db_user = await self._get_user_from_db(user.name, as_class=UserGetRespModel)

        if not db_user:
            raise HTTPException(status_code=400, detail="錯誤的使用者名稱或密碼")

        check = check_password(user.password.encode("utf-8"), db_user.password.encode("utf-8"))

        if check:
            session_id = str(uuid4())
            await create_session(
                session_id,
                {"user_id": str(db_user.name), "role": db_user.is_admin},
                expires=60,
            )
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                secure=False,
                max_age=60 * 60 * 24
            )
        else:
            raise HTTPException(status_code=400, detail="錯誤的使用者名稱或密碼")

    @staticmethod
    async def logout(response: Response, session_id: str | None = None) -> None:
        if session_id:
            await delete_session(session_id)
        response.delete_cookie("session_id")

    async def _get_user_from_db(self, name: str, as_class: Type[T] = None) -> T:
        """
        從資料庫取得使用者資訊

        :param name: 使用者名稱
        :return:
        """
        stmt = select(User).select_from(User).where(User.name == name)
        result = await self._session.execute(stmt)
        user = result.scalars().one_or_none()

        if not user:
            raise Missing(msg="無此名稱!")

        if as_class:
            return as_class.model_validate(user)
        else:
            return user
