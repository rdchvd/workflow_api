from pydantic import EmailStr, Field
from pydantic.dataclasses import dataclass


@dataclass
class TokenSerializer:
    access: str
    refresh: str


@dataclass
class RefreshTokenSerializer:
    refresh: str


@dataclass
class CredentialsSerializer:
    password: str
    email: EmailStr = Field(default_factory=EmailStr)
