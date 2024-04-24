from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.serializers.auth import CredentialsSerializer, TokenSerializer
from app.serializers.users import UserSerializer
from app.services.auth import AuthService
from app.services.users import UserService
from core.db import get_session

auth_router = APIRouter(tags=["auth"])


class AuthViewSet:
    @staticmethod
    @auth_router.post("/login/", response_model=TokenSerializer)
    async def login(
        credentials: CredentialsSerializer,
        db: Session = Depends(get_session),
    ) -> TokenSerializer:
        return await AuthService.login(db=db, credentials=credentials.__dict__)

    @staticmethod
    @auth_router.post("/register/", response_model=UserSerializer)
    async def register(user_data: CredentialsSerializer, db: Session = Depends(get_session)) -> UserSerializer:
        """Registers user and returns token."""
        return await UserService.create_user(db=db, data=user_data.__dict__)
