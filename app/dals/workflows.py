from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.users import User
from app.models.workflows import Workflow


class WorkflowDAL:
    def __init__(self, db: Session, current_user: Optional[User] = None) -> None:
        self.db = db
        self.user = current_user

    def get_base_query(self, on_update=False):
        is_creator = Workflow.created_by == self.user.id
        can_edit = Workflow.can_edit.contains(self.user.id)
        can_view = Workflow.can_view.contains(self.user.id)
        if on_update:
            return select(Workflow).filter(is_creator | can_edit)
        return select(Workflow).filter(is_creator | can_edit | can_view)

    def get_workflow(self, workflow_id: str):
        query = self.get_base_query().filter(Workflow.id == workflow_id)
        workflow = self.db.execute(query).scalar()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow

    def list_workflows(self):
        query = self.get_base_query()
        return self.db.execute(query).scalars()

    def create_workflow(self, create_data: dict):
        workflow = Workflow(**create_data, created_by=self.user.id)
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def update_workflow(self, workflow_id: str, update_data: dict):
        workflow = self.get_workflow(workflow_id)
        for key, value in update_data.items():
            setattr(workflow, key, value)

        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def delete_workflow(self, workflow_id: str):
        workflow = self.get_workflow(workflow_id)
        self.db.delete(workflow)
        self.db.commit()
