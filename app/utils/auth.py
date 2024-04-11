from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBearer, OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.dals.users import UserDAL
from core.db import get_session
from settings import HASH_NAME_ALGORITHM, JWT_SECRET_KEY


def authenticate(db: Session, authorization: str = Depends(OAuth2()), token: str = Depends(HTTPBearer())):
    """Extracts token from authorization header and raises error if invalid."""
    _, token = get_authorization_scheme_param(authorization)

    try:
        user_data = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=HASH_NAME_ALGORITHM)
        return UserDAL(db=db).get_user_by_email(
            email=user_data["email"], error={"status_code": HTTP_401_UNAUTHORIZED, "detail": "Invalid API Key"}
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )


def get_current_user(db: Session = Depends(get_session), authorization: Optional[str] = Header(default="")):
    """Returns user from db if token in header given."""
    if authorization:
        return authenticate(db=db, authorization=authorization)


def get_auth_header(authorization: str = Depends(HTTPBearer())):
    """Add authorization as a required pard of router, but don't check if it's correct."""
    return authorization
