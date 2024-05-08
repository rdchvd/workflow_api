from collections import defaultdict
from typing import Optional, Union
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.users import Permission, PermissionType, User
from app.models.workflows import (
    ConditionNodeConfiguration,
    EndNodeConfiguration,
    MessageNodeConfiguration,
    Node,
    NodeType,
    StartNodeConfiguration,
    Workflow,
)


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

    async def get_base_query(self, on_update=False, on_delete=False, select_fields=None):
        is_creator = Workflow.created_by == self.user.id
        user_workflows = await self.get_workflows_by_permissions()

        can_edit = Workflow.id.in_(user_workflows.get(PermissionType.edit.value, []))
        can_view = Workflow.id.in_(user_workflows.get(PermissionType.view.value, []))
        can_delete = Workflow.id.in_(user_workflows.get(PermissionType.delete.value, []))

        fields = select_fields or [Workflow]

        if on_delete:
            return select(*fields).filter(is_creator | can_delete)

        if on_update:
            return select(*fields).filter(is_creator | can_edit)

        return select(*fields).filter(is_creator | can_edit | can_view | can_delete)

    async def get_workflow(self, workflow_id: Union[UUID, str], *args, **kwargs):
        query = await self.get_base_query(*args, **kwargs)
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
        await self.db.refresh(workflow)
        return workflow

    async def update_workflow(self, workflow_id: str, update_data: dict):
        workflow = await self.get_workflow(workflow_id, on_update=True)
        for key, value in update_data.items():
            if value is None:
                continue
            setattr(workflow, key, value)

        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete_workflow(self, workflow_id: str):
        workflow = await self.get_workflow(workflow_id, on_delete=True)
        await self.db.delete(workflow)
        await self.db.commit()


class NodeDAL:
    ConfigurationModel = None
    node_type = None
    all_configs = [
        StartNodeConfiguration,
        MessageNodeConfiguration,
        ConditionNodeConfiguration,
        EndNodeConfiguration,
    ]

    def __init__(self, db: Session, current_user: Optional[User] = None) -> None:
        self.db = db
        self.user = current_user

    def _create_node(self, node_data: dict):
        node_data["node_type"] = self.node_type
        node = Node(**node_data, created_by=self.user.id)
        self.db.add(node)
        return node

    def _create_node_configuration(self, node_id: str, configuration_data: dict):
        configuration_data["node_id"] = node_id
        configuration_data["created_by"] = self.user.id
        node_configuration = self.ConfigurationModel(**configuration_data)
        self.db.add(node_configuration)
        return node_configuration

    async def create_node(self, node_data: dict, configuration_data: dict):
        node = self._create_node(node_data)
        await self.db.flush()

        config = self._create_node_configuration(node.id, configuration_data)

        await self.db.commit()
        await self.db.refresh(node)

        return node, config

    async def get_node(self, node_id: Union[UUID, str], workflow_id: Union[UUID, str]):
        query = select(Node).filter(Node.id == node_id, Node.workflow_id == workflow_id)

        node = await self.db.execute(query)
        node = node.scalar()
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return node

    async def list_nodes(self, workflow_id: Union[UUID, str]):
        query = select(Node).filter(Node.workflow_id == workflow_id)
        nodes = await self.db.execute(query)
        return nodes.scalars().all()

    async def update_node(self, node_id: Union[UUID, str], workflow_id: Union[UUID, str], update_data: dict):
        node = await self.get_node(node_id, workflow_id)
        config = node.config
        for key, value in update_data.items():
            setattr(config, key, value)

        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def delete_node(self, node_id: Union[UUID, str], workflow_id: Union[UUID, str]):
        node = await self.get_node(node_id, workflow_id)
        await self.db.delete(node)
        await self.db.commit()


class StartNodeDAL(NodeDAL):
    ConfigurationModel = StartNodeConfiguration
    node_type = NodeType.start


class MessageNodeDAL(NodeDAL):
    ConfigurationModel = MessageNodeConfiguration
    node_type = NodeType.message


class ConditionNodeDAL(NodeDAL):
    ConfigurationModel = ConditionNodeConfiguration
    node_type = NodeType.condition


class EndNodeDAL(NodeDAL):
    ConfigurationModel = EndNodeConfiguration
    node_type = NodeType.end
