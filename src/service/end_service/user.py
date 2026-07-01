from custom_select.select import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import User
from src.vm.end.user_vm import EndUserGetReqModel, EndUserRespModel


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