from typing import Any, Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dals.workflows import WorkflowDAL
from app.models.users import User
from app.serializers.workflows import (
    WorkflowSerializer,
    WorkflowUpdateSerializer,
)


class WorkflowService:
    DAL = WorkflowDAL

    @classmethod
    async def retrieve(cls, db: Session, _id: str, user: User = None):
        data = cls.DAL(db=db, current_user=user).get_workflow(_id)
        return WorkflowSerializer(**data)

    @classmethod
    async def list(cls, db: Session, user: User):
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        workflows = await cls.DAL(db=db, current_user=user).list_workflows()
        return [workflow.__dict__ for workflow in workflows]

    @classmethod
    async def create(cls, db: Session, data: Dict[str, Any], user: User = None):
        return await cls.DAL(db=db, current_user=user).create_workflow(create_data=data)

    @classmethod
    async def update(cls, db: Session, _id: str, data: WorkflowUpdateSerializer, user: User = None):
        validated_data = WorkflowUpdateSerializer(**data)
        return cls.DAL(db=db, current_user=user).update_workflow(workflow_id=_id, update_data=validated_data.dict())

    @classmethod
    async def delete(cls, db: Session, _id: str, user: User = None):
        return cls.DAL(db=db, current_user=user).delete_workflow(workflow_id=_id)
