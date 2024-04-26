from typing import Any, Dict, Optional, Type, Union
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dals.workflows import ConditionNodeDAL, EndNodeDAL, MessageNodeDAL, NodeDAL, StartNodeDAL, WorkflowDAL
from app.models import Workflow
from app.models.users import User
from app.models.workflows import BaseNodeConfiguration, Node


class WorkflowService:
    DAL = WorkflowDAL

    @classmethod
    async def retrieve(cls, db: Session, _id: Union[str, UUID], user: User = None):
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
    async def update(cls, db: Session, _id: Union[str, UUID], data: Dict[str, Any], user: User = None):
        workflow = await cls.DAL(db=db, current_user=user).update_workflow(workflow_id=_id, update_data=data)
        return workflow.__dict__

    @classmethod
    async def delete(cls, db: Session, _id: Union[str, UUID], user: User = None):
        return await cls.DAL(db=db, current_user=user).delete_workflow(workflow_id=_id)


class NodeService:
    DAL = NodeDAL

    @staticmethod
    def _get_dict(node: Optional[Node], config: Type[BaseNodeConfiguration] = None) -> Dict[str, Any]:
        config = config or node.config
        return {**config.__dict__, **node.__dict__}

    @staticmethod
    def _get_node_data(workflow_id: UUID):
        return {"workflow_id": workflow_id}

    @staticmethod
    def _get_node_configuration_data(data: Dict[str, Any]):
        return data

    @classmethod
    async def create(cls, db: Session, workflow_id: UUID, data: Dict[str, Any], user: User = None):
        await WorkflowDAL(db, user).get_workflow(workflow_id, on_update=True, select_fields=[Workflow.id])

        node = cls._get_node_data(workflow_id)
        config = cls._get_node_configuration_data(data)
        node, config = await cls.DAL(db=db, current_user=user).create_node(node_data=node, configuration_data=config)
        return cls._get_dict(node, config)

    @classmethod
    async def retrieve(cls, db: Session, workflow_id: Union[str, UUID], node_id: Union[str, UUID], user: User = None):
        node = await cls.DAL(db=db, current_user=user).get_node(workflow_id=workflow_id, node_id=node_id)
        return cls._get_dict(node)

    @classmethod
    async def list(cls, db: Session, workflow_id: Union[str, UUID], user: User = None):
        nodes = await cls.DAL(db=db, current_user=user).list_nodes(workflow_id=workflow_id)
        return [node.__dict__ for node in nodes]

    @classmethod
    async def update(
        cls,
        db: Session,
        workflow_id: Union[str, UUID],
        node_id: Union[str, UUID],
        data: Dict[str, Any],
        user: User = None,
    ):
        config = await cls.DAL(db=db, current_user=user).update_node(
            workflow_id=workflow_id, node_id=node_id, update_data=data
        )
        return cls._get_dict(config.node, config)

    @classmethod
    async def delete(cls, db: Session, workflow_id: Union[str, UUID], node_id: Union[str, UUID], user: User = None):
        return await cls.DAL(db=db, current_user=user).delete_node(workflow_id=workflow_id, node_id=node_id)


class StartNodeService(NodeService):
    DAL = StartNodeDAL


class MessageNodeService(NodeService):
    DAL = MessageNodeDAL


class ConditionNodeService(NodeService):
    DAL = ConditionNodeDAL


class EndNodeService(NodeService):
    DAL = EndNodeDAL
