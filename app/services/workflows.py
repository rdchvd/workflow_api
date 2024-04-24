from typing import Any, Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dals.workflows import WorkflowDAL
from app.models.users import User


class WorkflowService:
    DAL = WorkflowDAL

    @classmethod
    async def retrieve(cls, db: Session, _id: str, user: User = None):
        workflow = await cls.DAL(db=db, current_user=user).get_workflow(workflow_id=_id)
        return workflow.__dict__

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
    async def update(cls, db: Session, _id: str, data: Dict[str, Any], user: User = None):
        workflow = await cls.DAL(db=db, current_user=user).update_workflow(workflow_id=_id, update_data=data)
        return workflow.__dict__

    @classmethod
    async def delete(cls, db: Session, _id: str, user: User = None):
        return await cls.DAL(db=db, current_user=user).delete_workflow(workflow_id=_id)
