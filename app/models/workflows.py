import enum
from typing import Set
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.models.base import BaseModel


class Workflow(BaseModel):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    @declared_attr
    def can_view(self) -> Mapped[Set["User"]]:
        return relationship("User", back_populates="workflows_to_view")

    @declared_attr
    def can_edit(self) -> Mapped[Set["User"]]:
        return relationship("User", back_populates="workflows_to_edit")


class NodeType(enum.Enum):
    start = "start"
    message = "message"
    condition = "condition"
    end = "end"


class Node(BaseModel):
    __tablename__ = "nodes"

    node_type: Mapped[NodeType] = mapped_column(nullable=False)

    workflow_id: Mapped[UUID] = mapped_column(ForeignKey("workflows.id"), nullable=False)

    @declared_attr
    def workflow(self) -> Mapped["Workflow"]:
        return relationship("Workflow", foreign_keys=[self.workflow_id])


class EdgeWeight(enum.Enum):
    zero = 0
    yes = 1
    no = -1


class Edge(BaseModel):
    __tablename__ = "edges"

    status: Mapped[EdgeWeight] = mapped_column(nullable=False)

    source_node_id: Mapped[UUID] = mapped_column(ForeignKey("nodes.id"), nullable=False)
    target_node_id: Mapped[UUID] = mapped_column(ForeignKey("nodes.id"), nullable=False)

    __table_args__ = (UniqueConstraint("source_node_id", "target_node_id"),)

    @declared_attr
    def source_node(self) -> Mapped["Node"]:
        return relationship("Node", foreign_keys=[self.source_node_id])

    @declared_attr
    def target_node(self) -> Mapped["Node"]:
        return relationship("Node", foreign_keys=[self.target_node_id])


class BaseNodeConfiguration(BaseModel):
    __abstract__ = True

    node_id: Mapped[UUID] = mapped_column(ForeignKey("nodes.id"), nullable=False)

    # __table_args__ = (UniqueConstraint("node_id"),)

    class Meta:
        abstract = True
        table_args = (UniqueConstraint("node_id"),)

    @declared_attr
    def node(self) -> Mapped["Node"]:
        return relationship("Node", foreign_keys=[self.node_id])


class StartNodeConfiguration(BaseNodeConfiguration):
    __tablename__ = "start_node_configurations"


class NodeStatus(enum.Enum):
    pending = "pending"
    sent = "sent"
    opened = "opened"


class MessageNodeConfiguration(BaseNodeConfiguration):
    __tablename__ = "message_node_configurations"

    status: Mapped[NodeStatus] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(nullable=False)


class ConditionNodeConfiguration(BaseNodeConfiguration):
    __tablename__ = "condition_node_configurations"


class EndNodeConfiguration(BaseNodeConfiguration):
    __tablename__ = "end_node_configurations"
