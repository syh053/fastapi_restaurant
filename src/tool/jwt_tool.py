from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError

from db.model.database import db_config


def create_access_token(user_id: str, is_admin: bool) -> str:
    payload = {
        "sub": user_id,
        "role": is_admin,
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=1)
    }
    return jwt.encode(payload, db_config["SECRET"]["secret_key"], algorithm=db_config["SECRET"]["algorithm"])


def decode_access_token(token: str) -> dict[str, bool]:
    try:
        return jwt.decode(token, db_config["SECRET"]["secret_key"], algorithms=[db_config["SECRET"]["algorithm"]])

    except ExpiredSignatureError:
        raise Exception("Token 已過期")

    except JWTError:
        raise Exception("Token 無效或被竄改")
