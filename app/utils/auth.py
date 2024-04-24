from typing import Optional

from fastapi import Depends, Header
from fastapi.security import HTTPBearer, OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session

from app.dals.users import UserDAL
from app.services.auth import JWTService
from core.db import get_session
from settings import JWT_SECRET_KEY


async def authenticate(db: Session, authorization: str = Depends(OAuth2()), token: str = Depends(HTTPBearer())):
    """Extracts token from authorization header and raises error if invalid."""
    _, token = get_authorization_scheme_param(authorization)
    user_data = JWTService.decode_token(token=token, key=JWT_SECRET_KEY)
    return await UserDAL(db=db).get_user(user_id=user_data["user_id"])


async def get_current_user(db: Session = Depends(get_session), authorization: Optional[str] = Header(default="")):
    """Returns user from db if token in header given."""
    if authorization:
        return await authenticate(db=db, authorization=authorization)
    return None


def get_auth_header(authorization: str = Depends(HTTPBearer())):
    """Add authorization as a required pard of router, but don't check if it's correct."""
    return authorization
