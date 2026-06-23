import json
from redis.asyncio import Redis
from db.model.database import db_config

redis_client = Redis(
    host=db_config["REDIS"]["host"],
    port=int(db_config["REDIS"]["port"]),
    db=int(db_config["REDIS"]["db"]),
    password=db_config["REDIS"].get("password") or None,
    decode_responses=True,
    protocol=2,
)


async def create_session(session_id: str, data: dict, expires: int = 86400) -> None:
    await redis_client.set(f"session:{session_id}", json.dumps(data), ex=expires)


async def get_session(session_id: str) -> dict | None:
    raw = await redis_client.get(f"session:{session_id}")
    return json.loads(raw) if raw else None


async def delete_session(session_id: str) -> None:
    await redis_client.delete(f"session:{session_id}")
