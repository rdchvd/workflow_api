from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import select

from app.models.users import User


class UserDAL:
    def __init__(self, db, user: User = None):
        self.db = db
        self.user = user

    @staticmethod
    def get_base_query():
        return select(User)

    async def get_user(self, user_id):
        query = self.get_base_query().filter(User.id == user_id)
        user = await self.db.execute(query)
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return user

    async def get_user_by_email(self, email: str, error: Optional[Dict[str, Any]] = None):
        query = self.get_base_query().filter(User.email == email)
        user = await self.db.execute(query)
        user = user.scalars().first()
        if not user:
            base_error = {"status_code": 404, "detail": "User not found"}
            base_error.update(error or {})
            raise HTTPException(**base_error)
        return user

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        return user
