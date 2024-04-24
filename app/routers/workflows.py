from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.users import User
from app.serializers.workflows import (
    WorkflowCreateSerializer,
    WorkflowListSerializer,
    WorkflowSerializer,
    WorkflowUpdateSerializer,
)
from app.services.workflows import WorkflowService
from app.utils.auth import get_current_user
from core.db import get_session

workflows_router = APIRouter(tags=["workflows"])


class WorkflowViewSet:
    @staticmethod
    @workflows_router.get("/{workflow_id}/", response_model=WorkflowSerializer)
    async def retrieve_workflow(
        workflow_id: str,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_session),
    ) -> WorkflowSerializer:
        return await WorkflowService.retrieve(db=db, _id=workflow_id, user=user)

    @staticmethod
    @workflows_router.get("/", response_model=WorkflowListSerializer)
    async def list_workflows(user: User = Depends(get_current_user), db=Depends(get_session)) -> WorkflowListSerializer:
        workflows = await WorkflowService.list(db=db, user=user)
        return WorkflowListSerializer(workflows=workflows)

    @staticmethod
    @workflows_router.post("/", response_model=None)
    async def create_workflow(
        workflow_data: WorkflowCreateSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await WorkflowService.create(db=db, data=workflow_data.__dict__, user=user)

    @staticmethod
    @workflows_router.patch("/{workflow_id}/", response_model=None)
    async def update_workflow(
        workflow_id: str,
        workflow_data: WorkflowUpdateSerializer,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await WorkflowService.update(db=db, _id=workflow_id, data=workflow_data, user=user)

    @staticmethod
    @workflows_router.delete("/{workflow_id}/", response_model=None)
    async def delete_workflow(
        workflow_id: str,
        user: User = Depends(get_current_user),
        db=Depends(get_session),
    ):
        return await WorkflowService.delete(db=db, _id=workflow_id, user=user)
