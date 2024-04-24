from collections import defaultdict
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.users import Permission, PermissionType, User
from app.models.workflows import Workflow


class WorkflowDAL:
    def __init__(self, db: Session, current_user: Optional[User] = None) -> None:
        self.db = db
        self.user = current_user

    async def get_workflows_by_permissions(self):
        query = select(Permission.id, Permission.workflow_id).filter(Permission.user_id == self.user.id)
        permissions = await self.db.execute(query)

        workflows_by_permissions = defaultdict(set)
        for permission in permissions:
            workflows_by_permissions[permission.permission].add(permission.workflow_id)

        return workflows_by_permissions

    async def get_base_query(self, on_update=False, on_delete=False):
        is_creator = Workflow.created_by == self.user.id
        user_workflows = await self.get_workflows_by_permissions()

        can_edit = Workflow.id.in_(user_workflows.get(PermissionType.edit.value, []))
        can_view = Workflow.id.in_(user_workflows.get(PermissionType.view.value, []))
        can_delete = Workflow.id.in_(user_workflows.get(PermissionType.delete.value, []))

        if on_delete:
            return select(Workflow).filter(is_creator | can_delete)

        if on_update:
            return select(Workflow).filter(is_creator | can_edit)

        return select(Workflow).filter(is_creator | can_edit | can_view | can_delete)

    async def get_workflow(self, workflow_id: str):
        query = await self.get_base_query()
        workflow = await self.db.execute(query.filter(Workflow.id == workflow_id))
        workflow = workflow.scalar()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow

    async def list_workflows(self):
        query = await self.get_base_query()
        workflows = await self.db.execute(query)
        return workflows.scalars().all()

    async def create_workflow(self, create_data: dict):
        workflow = Workflow(**create_data, created_by=self.user.id)
        self.db.add(workflow)
        await self.db.commit()
        self.db.refresh(workflow)
        return workflow

    async def update_workflow(self, workflow_id: str, update_data: dict):
        workflow = await self.get_workflow(workflow_id)
        for key, value in update_data.items():
            setattr(workflow, key, value)

        await self.db.commit()
        self.db.refresh(workflow)
        return workflow

    async def delete_workflow(self, workflow_id: str):
        workflow = await self.get_workflow(workflow_id)
        await self.db.delete(workflow)
        await self.db.commit()
