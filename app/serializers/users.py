from uuid import UUID

from pydantic import EmailStr
from pydantic.dataclasses import dataclass


@dataclass
class UserSerializer:
    id: UUID
    email: EmailStr
