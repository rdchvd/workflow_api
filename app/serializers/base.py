from typing import Optional

from fastapi import Query
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class BaseResponseSerializer(BaseModel):
    class Config:
        from_attributes = True
        read_with_orm_mode = True


@dataclass
class BaseRequestSerializer:
    search: Optional[str] = Query(None)
    order_by: Optional[str] = Query(None)
