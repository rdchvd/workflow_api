from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(AsyncAttrs, DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[UUID] = mapped_column(nullable=True)

    class Meta:
        abstract = True
        arbitrary_types_allowed = True
