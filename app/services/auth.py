import json
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple
from uuid import uuid4

from fastapi import HTTPException
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.dals.users import UserDAL
from app.services.users import UserService
from settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    HASH_NAME_ALGORITHM,
    JWT_REFRESH_SECRET_KEY,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)


class JWTService:
    @staticmethod
    def encode_token(data: Dict[str, Any], secret_key: str) -> str:
        data = json.loads(json.dumps(data, default=str))
        return jwt.encode(data, secret_key, HASH_NAME_ALGORITHM)

    @classmethod
    def create_tokens(cls, data: Dict[str, Any]) -> Tuple[str, str]:
        """Creates JWT-tokens."""
        now_time = datetime.utcnow()
        access_expires = now_time + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_expires = now_time + timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))

        iat = int(now_time.timestamp())
        access_expires = int(access_expires.timestamp())
        refresh_expires = int(refresh_expires.timestamp())

        access_data = {**data, "jti": uuid4(), "iat": iat, "exp": access_expires, "token_type": "access"}
        refresh_data = {**data, "jti": uuid4(), "iat": iat, "exp": refresh_expires, "token_type": "refresh"}

        access_token = cls.encode_token(access_data, JWT_SECRET_KEY)
        refresh_token = cls.encode_token(refresh_data, JWT_REFRESH_SECRET_KEY)
        return access_token, refresh_token

    @staticmethod
    def decode_token(token, key):
        """Decodes JWT-token."""
        try:
            return jwt.decode(token, algorithms=HASH_NAME_ALGORITHM, key=key)
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired.")
        except JWTError:
            raise HTTPException(status_code=401, detail="Incorrect token type.")


class AuthService:
    @staticmethod
    async def login(db: Session, credentials: dict):
        """Logs in user and returns token."""
        user = await UserDAL(db=db).get_user_by_email(
            email=credentials["email"], error={"status_code": 401, "detail": "Incorrect email or password"}
        )
        if user and UserService.verify_password(plain_password=credentials["password"], hashed_password=user.password):
            access_token, refresh_token = JWTService.create_tokens(data={"user_id": user.id})
            return dict(access=access_token, refresh=refresh_token)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    @staticmethod
    async def refresh_tokens(db: Session, refresh_token: str):
        """Refreshes access tokens."""

        refresh_data = JWTService.decode_token(refresh_token, JWT_REFRESH_SECRET_KEY)
        user = await UserDAL(db=db).get_user(user_id=refresh_data["user_id"])
        if user:
            access_token, refresh_token = JWTService.create_tokens(data=refresh_data)
            return dict(access=access_token, refresh=refresh_token)

        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
