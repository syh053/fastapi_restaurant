from uuid import UUID

from custom_select.select import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Cart, MenuItem, Restaurant
from src.vm.cart.cart_vm import CartItemRespModel, CartRespModel


class CartGetService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_cart(self, user_id: UUID) -> tuple[list[CartItemRespModel], int]:
        """
        取得指定使用者的購物車內容

        :param user_id: 使用者 ID
        :return: (購物車品項列表, 總金額)
        """
        stmt = (
            select(
                Cart.id,
                Cart.quantity,
                MenuItem.id.label("menu_item_id"),
                MenuItem.name,
                MenuItem.price,
                MenuItem.image,
                MenuItem.restaurant_id,
                Restaurant.name.label("restaurant_name"),
                Cart.created_at,
                Cart.updated_at,
            )
            .select_from(Cart)
            .join(MenuItem, MenuItem.id == Cart.menu_item_id)
            .outerjoin(Restaurant, Restaurant.id == MenuItem.restaurant_id)
            .where(Cart.user_id == user_id)
            .order_by(Cart.created_at)
        )
        results = await self._session.execute(stmt)
        rows = results.all()

        items = [
            CartItemRespModel(**row._mapping, subtotal=row.price * row.quantity)
            for row in rows
        ]
        total = sum(item.subtotal for item in items)

        return items, total

    async def get_cart_response(self, user_id: UUID) -> dict:
        """
        取得購物車內容並包裝成統一回應格式

        :param user_id: 使用者 ID
        :return: 回傳購物車品項列表與總金額
        """
        items, total = await self.get_cart(user_id)

        return {
            "code": 200,
            "message": "查詢購物車成功!",
            "data": CartRespModel(items=items, total=total)
        }

    async def _get_menu_item(self, menu_item_id: UUID) -> MenuItem | None:
        stmt = select(MenuItem).where(MenuItem.id == menu_item_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_cart_restaurant_id(self, user_id: UUID) -> UUID | None:
        stmt = (
            select(MenuItem.restaurant_id)
            .select_from(Cart)
            .join(MenuItem, MenuItem.id == Cart.menu_item_id)
            .where(Cart.user_id == user_id)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_cart_item_by_menu(self, user_id: UUID, menu_item_id: UUID) -> Cart | None:
        stmt = select(Cart).where(Cart.user_id == user_id, Cart.menu_item_id == menu_item_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_cart_item_by_id(self, user_id: UUID, cart_item_id: UUID) -> Cart | None:
        stmt = select(Cart).where(Cart.id == cart_item_id, Cart.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
