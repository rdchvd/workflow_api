from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.users import User
from app.serializers.workflows import (
    ConditionNodeCreateSerializer,
    EndNodeCreateSerializer,
    MessageNodeCreateSerializer,
    NodeBaseSerializer,
    NodeListSerializer,
    StartNodeCreateSerializer,
    WorkflowCreateSerializer,
    WorkflowListSerializer,
    WorkflowSerializer,
    WorkflowUpdateSerializer,
)
from app.services.workflows import (
    ConditionNodeService,
    EndNodeService,
    MessageNodeService,
    NodeService,
    StartNodeService,
    WorkflowService,
)
from app.utils.auth import get_current_user
from core.db import get_session

workflows_router = APIRouter(tags=["workflows"], prefix="/workflows")
nodes_router = APIRouter(tags=["nodes"], prefix="/workflows/{workflow_id}/nodes")


class WorkflowViewSet:
    @staticmethod
    @workflows_router.get("/{workflow_id}/", response_model=WorkflowSerializer)
    async def retrieve_workflow(
        workflow_id: UUID,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_session),
    ) -> WorkflowSerializer:
        workflow = await WorkflowService.retrieve(db=db, _id=workflow_id, user=user)
        return WorkflowSerializer(**workflow)

    @staticmethod
    @workflows_router.get("/", response_model=WorkflowListSerializer)
    async def list_workflows(user: User = Depends(get_current_user), db=Depends(get_session)) -> WorkflowListSerializer:
        workflows = await WorkflowService.list(db=db, user=user)
        return WorkflowListSerializer(workflows=workflows)

    @staticmethod
    @workflows_router.post("/", response_model=WorkflowSerializer, status_code=201)
    async def create_workflow(
        workflow_data: WorkflowCreateSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await WorkflowService.create(db=db, data=workflow_data.__dict__, user=user)

    @staticmethod
    @workflows_router.patch("/{workflow_id}/", response_model=WorkflowSerializer)
    async def update_workflow(
        workflow_id: UUID,
        workflow_data: WorkflowUpdateSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await WorkflowService.update(db=db, _id=workflow_id, data=workflow_data.__dict__, user=user)

    @staticmethod
    @workflows_router.delete("/{workflow_id}/", response_model=None, status_code=204)
    async def delete_workflow(
        workflow_id: UUID,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await WorkflowService.delete(db=db, _id=workflow_id, user=user)


class NodeViewSet:
    @staticmethod
    @nodes_router.post("/start/", response_model=NodeBaseSerializer, response_model_exclude_none=True)
    async def create_start_node(
        workflow_id: UUID,
        node_data: StartNodeCreateSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await StartNodeService.create(db=db, workflow_id=workflow_id, data=node_data.__dict__, user=user)

    @staticmethod
    @nodes_router.post("/message/", response_model=NodeBaseSerializer, response_model_exclude_none=True)
    async def create_message_node(
        workflow_id: UUID,
        node_data: MessageNodeCreateSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await MessageNodeService.create(db=db, workflow_id=workflow_id, data=node_data.__dict__, user=user)

    @staticmethod
    @nodes_router.post("/condition/", response_model=NodeBaseSerializer, response_model_exclude_none=True)
    async def create_condition_node(
        workflow_id: UUID,
        node_data: ConditionNodeCreateSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await ConditionNodeService.create(db=db, workflow_id=workflow_id, data=node_data.__dict__, user=user)

    @staticmethod
    @nodes_router.post("/end/", response_model=NodeBaseSerializer, response_model_exclude_none=True)
    async def create_end_node(
        workflow_id: UUID,
        node_data: EndNodeCreateSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await EndNodeService.create(db=db, workflow_id=workflow_id, data=node_data.__dict__, user=user)

    @staticmethod
    @nodes_router.get("/{node_id}/", response_model=NodeBaseSerializer, response_model_exclude_none=True)
    async def retrieve_node(
        workflow_id: UUID,
        node_id: UUID,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await NodeService.retrieve(db=db, workflow_id=workflow_id, node_id=node_id, user=user)

    @staticmethod
    @nodes_router.get("/", response_model=NodeListSerializer, response_model_exclude_none=True)
    async def list_nodes(
        workflow_id: UUID,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        nodes = await NodeService.list(db=db, workflow_id=workflow_id, user=user)
        return NodeListSerializer(nodes=nodes)

    @staticmethod
    @nodes_router.patch("/{node_id}/", response_model=NodeBaseSerializer, response_model_exclude_none=True)
    async def update_node(
        workflow_id: UUID,
        node_id: UUID,
        node_data: NodeBaseSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await NodeService.update(
            db=db, workflow_id=workflow_id, node_id=node_id, data=node_data.__dict__, user=user
        )

    @staticmethod
    @nodes_router.delete("/{node_id}/", response_model=None)
    async def delete_node(
        workflow_id: UUID,
        node_id: UUID,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await NodeService.delete(db=db, workflow_id=workflow_id, node_id=node_id, user=user)
