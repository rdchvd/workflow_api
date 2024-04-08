from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import EmailType

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[EmailType] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=True)


