import uuid

import bcrypt
from fastapi import HTTPException, Cookie, Depends
from fastapi.security import OAuth2PasswordBearer

from db.model.enums import UserRole
from src.tool.redis_client import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def check_password(password: bytes, db_password: bytes):
    return bcrypt.checkpw(password, db_password)


async def get_current_user(session_id: str | None = Cookie(default=None)) -> dict:
    if not session_id:
        raise HTTPException(status_code=401, detail="未傳入會話")

    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="無此會話，或會話過期")

    return session


def _normalize_role(role) -> str | None:
    """相容舊 session:布林 True 視為超級管理員，False 視為一般使用者"""
    if role is True:
        return UserRole.SUPER_ADMIN
    if role is False or role is None:
        return UserRole.USER
    return role


def require_roles(*roles: UserRole, detail: str = "無權限進入後台"):
    """
    建立角色檢查依賴

    :param roles: 允許的角色
    :param detail: 無權限時的錯誤訊息
    """

    def checker(user=Depends(get_current_user)):
        if _normalize_role(user.get("role")) not in roles:
            raise HTTPException(status_code=403, detail=detail)
        return user

    return checker


# 僅超級管理員
require_admin = require_roles(UserRole.SUPER_ADMIN)
# 僅業者(營業額等業者專屬功能，超級管理員也不可存取)
require_owner = require_roles(UserRole.OWNER, detail="僅業者可查看營業額")
# 超級管理員或業者(餐廳、菜單後台管理)
require_admin_or_owner = require_roles(UserRole.SUPER_ADMIN, UserRole.OWNER)


def get_owner_scope(user: dict) -> uuid.UUID | None:
    """
    取得資料範圍限制：業者回傳自己的 user_id（僅能操作自己的餐廳），超級管理員回傳 None（不限制）
    """
    if _normalize_role(user.get("role")) == UserRole.OWNER:
        return uuid.UUID(user["user_id"])
    return None
