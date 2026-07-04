from custom_select.select import select
from errors import Missing
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import User
from src.vm.end.user_vm import EndUserGetReqModel, EndUserRespModel, EndUserUpdateReqModel


class UserCrud:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_users(self, params: EndUserGetReqModel) -> tuple[list[EndUserRespModel], int]:
        stmt = (
            select(User, func.count(User.id).over().label("total"))
            .select_from(User)
            .where_if(params.name, lambda: User.name.ilike(f"%{params.name}%"))
            .where_if(params.email, lambda: User.email.ilike(f"%{params.email}%"))
            .where_if(params.is_admin is not None, lambda: User.is_admin == params.is_admin)
            .offset((params.current_page - 1) * params.page_size)
            .limit(params.page_size)
        )

        results = await self._session.execute(stmt)

        results = results.all()

        datas = [
            EndUserRespModel(**result[0].__dict__)
            for result in results
        ]

        total = results[0][1] if results else 0

        return datas, total

    async def update_user_access(self, params: EndUserUpdateReqModel) -> None:
        exist_check = await self._check_if_existed_user(params.id)

        if exist_check:
            update_data = params.model_dump()

            stmt = (
                update(User)
                .values(update_data)
                .where(User.id == params.id)
            )
            await self._session.execute(stmt)
            await self._session.commit()
        else:
            raise Missing(msg="使用者不存在")

    async def _check_if_existed_user(self, user_id):
        stmt = (
            select(User).where(User.id == user_id)
        )
        results = await self._session.scalar(stmt)

        if results:
            return True
        else:
            return False
