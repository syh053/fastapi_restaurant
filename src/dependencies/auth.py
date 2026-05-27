import bcrypt
from fastapi import HTTPException, Cookie, Depends
from fastapi.security import OAuth2PasswordBearer

from src.tool.jwt_tool import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def check_password(password: bytes, db_password: bytes):
    return bcrypt.checkpw(password, db_password)


async def get_current_user(access_token: str | None = Cookie(default=None)) -> dict[str, bool]:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return decode_access_token(access_token)


def require_admin(user=Depends(get_current_user)):
    if not user.get("role"):
        raise HTTPException(status_code=403, detail="無權限進入後台")
    return user
