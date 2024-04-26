from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field
from pydantic.dataclasses import dataclass

from app.models import NodeStatus


@dataclass
class WorkflowBaseSerializer:
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
        read_with_orm_mode = True


class WorkflowCreateSerializer(WorkflowBaseSerializer):
    pass


class WorkflowUpdateSerializer(WorkflowBaseSerializer):
    pass


@dataclass
class WorkflowSerializer:
    id: UUID4
    created_at: datetime
    updated_at: datetime
    created_by: UUID4
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
        read_with_orm_mode = True


class WorkflowListSerializer(BaseModel):
    workflows: List[WorkflowSerializer]


class NodeBaseSerializer(BaseModel):
    id: UUID4
    node_type: str
    workflow_id: UUID4
    status: Optional[NodeStatus] = Field(None)
    text: Optional[str] = Field(None)

    def get_status(self):
        print()
        return self.status


class NodeBaseCreateSerializer(BaseModel):
    pass


class StartNodeCreateSerializer(NodeBaseCreateSerializer):
    pass


class MessageNodeCreateSerializer(NodeBaseCreateSerializer):
    text: str
    status: Optional[NodeStatus]


class ConditionNodeCreateSerializer(NodeBaseCreateSerializer):
    pass


class EndNodeCreateSerializer(NodeBaseCreateSerializer):
    pass


class NodeListSerializer(BaseModel):
    nodes: List[NodeBaseSerializer]
