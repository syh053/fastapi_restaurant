from enum import StrEnum


class UserRole(StrEnum):
    """使用者角色"""
    USER = "user"
    OWNER = "owner"
    SUPER_ADMIN = "super_admin"
