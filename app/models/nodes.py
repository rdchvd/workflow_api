import enum
from typing import List, Set
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Workflow(BaseModel):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    can_view: Mapped[Set["users.User"]] = relationship(back_populates="workflows_to_view")
    can_edit: Mapped[Set["users.User"]] = relationship(back_populates="workflows_to_edit")


class NodeType(enum.Enum):
    start = "start"
    message = "message"
    condition = "condition"
    end = "end"


class Node(BaseModel):
    __tablename__ = "nodes"

    node_type: Mapped[NodeType] = mapped_column(nullable=False)

    workflow_id: Mapped[UUID] = mapped_column(ForeignKey("workflow.id"), nullable=False)
    workflow: Mapped["Workflow"] = relationship(back_populates="nodes")


class EdgeWeight(enum.Enum):
    zero = 0
    yes = 1
    no = -1


class Edge(BaseModel):
    __tablename__ = "edges"

    status: Mapped[EdgeWeight] = mapped_column(nullable=False)

    source_node_id: Mapped[UUID] = mapped_column(ForeignKey("node.id"), nullable=False)
    source_node: Mapped["Node"] = relationship("Node", foreign_keys=[source_node_id])

    target_node_id: Mapped[UUID] = mapped_column(ForeignKey("node.id"), nullable=False)
    target_node: Mapped["Node"] = relationship("Node", foreign_keys=[target_node_id])

    __table_args__ = (UniqueConstraint("source_node_id", "target_node_id"),)


class BaseNodeConfiguration(BaseModel):
    node_id: Mapped[UUID] = mapped_column(ForeignKey("node.id"), nullable=False, single_parent=True)
    node: Mapped["Node"] = relationship(back_populates="configuration")

    # __table_args__ = (UniqueConstraint("node_id"),)

    class Meta:
        abstract = True
        table_args = (UniqueConstraint("node_id"),)


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
