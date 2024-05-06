from typing import Any, Dict

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.dals.users import UserDAL


class UserService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, plain_password: str) -> str:
        return cls.pwd_context.hash(plain_password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    async def create_user(cls, db: Session, data: Dict[str, Any]):
        existing_user = await UserDAL(db).get_user_by_email(data["email"], raise_exception=False)
        if existing_user:
            raise HTTPException(detail="User with this email already exists", status_code=400)
        data["password"] = cls.hash_password(data["password"])
        user = await UserDAL(db).create_user(data)
        return user.__dict__
