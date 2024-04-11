from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import select

from app.models.users import User


class UserDAL:
    def __init__(self, db, user: User = None):
        self.db = db
        self.user = user

    def get_base_query(self):
        return select(User)

    def get_user(self, user_id):
        query = self.get_base_query().filter(User.id == user_id)
        user = self.db.execute(query).scalar()
        if not user:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return user

    def get_user_by_email(self, email: str, error: Optional[Dict[str, Any]] = None):
        query = self.get_base_query().filter(User.email == email)
        user = self.db.execute(query).scalar()
        if not user:
            error = error or {"status_code": 404, "detail": "User not found"}
            raise HTTPException(**error)
        return user
