from typing import List, Optional

from pydantic import UUID4, BaseModel
from pydantic.dataclasses import dataclass


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


class WorkflowSerializer(WorkflowBaseSerializer):
    id: UUID4
    created_at: str
    updated_at: str
    created_by: UUID4

    class Config:
        from_attributes = True


class WorkflowListSerializer(BaseModel):
    workflows: List[WorkflowSerializer]


class MessageNodeConfigurationBaseSerializer(BaseModel):
    text: str


class MessageNodeConfigurationCreateSerializer(MessageNodeConfigurationBaseSerializer):
    pass


class MessageNodeConfigurationUpdateSerializer(MessageNodeConfigurationBaseSerializer):
    pass


class MessageNodeConfigurationSerializer(MessageNodeConfigurationBaseSerializer):
    id: UUID4
    node_id: UUID4
    status: str

    class Config:
        from_attributes = True


class MessageNodeConfigurationListSerializer(BaseModel):
    message_node_configurations: List[MessageNodeConfigurationSerializer]
