import enum
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import EmailType

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(nullable=False, unique=True, type_=EmailType)
    password: Mapped[str] = mapped_column(nullable=True)


class PermissionType(enum.Enum):
    view = "view"
    edit = "edit"
    delete = "delete"


class Permission(BaseModel):
    __tablename__ = "permissions"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    workflow_id: Mapped[UUID] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    permission: Mapped[PermissionType] = mapped_column(nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "workflow_id", permission),)
