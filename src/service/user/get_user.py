from typing import TypeVar, Type

from fastapi import HTTPException
from fastapi import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model.user import User
from src.router.dependencies.auth import check_password
from src.tool.jwt_tool import create_access_token
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
            token = create_access_token(user_id=str(db_user.name), is_admin=db_user.is_admin)
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=60 * 60 * 24
            )
        else:
            raise HTTPException(status_code=400, detail="錯誤的使用者名稱或密碼")

    async def logout(self, response: Response) -> None:
        response.delete_cookie("access_token")

    async def _get_user_from_db(self, name: str, as_class: Type[T] = None) -> T:
        """
        從資料庫取得使用者資訊

        :param name: 使用者名稱
        :return:
        """
        stmt = select(User).select_from(User).where(User.name == name)
        result = await self._session.execute(stmt)
        user = result.scalars().one_or_none()

        if as_class:
            return as_class.model_validate(user)
        else:
            return user
