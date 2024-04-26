import enum

from sqlalchemy import UUID, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.models.base import BaseModel


class Workflow(BaseModel):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)


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

    @declared_attr
    def config(self) -> Mapped["BaseNodeConfiguration"]:
        return relationship("BaseNodeConfiguration", uselist=False, back_populates="node", lazy="selectin")


class BaseNodeConfiguration(BaseModel):
    __tablename__ = "node_configurations"

    node_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "nodes.id",
        ),
        nullable=False,
    )
    node_type: Mapped[NodeType] = mapped_column(nullable=False)

    __mapper_args__ = {"polymorphic_identity": "node_configuration", "polymorphic_on": node_type}

    class Meta:
        abstract = True
        table_args = (UniqueConstraint("node_id"),)

    @declared_attr
    def node(self) -> Mapped["Node"]:
        return relationship("Node", foreign_keys=[self.node_id], back_populates="config")


class StartNodeConfiguration(BaseNodeConfiguration):
    __tablename__ = "start_node_configurations"

    id = Column(UUID(as_uuid=True), ForeignKey("node_configurations.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": NodeType.start}


class NodeStatus(enum.Enum):
    pending = "pending"
    sent = "sent"
    opened = "opened"


class MessageNodeConfiguration(BaseNodeConfiguration):
    __tablename__ = "message_node_configurations"

    id = Column(UUID(as_uuid=True), ForeignKey("node_configurations.id"), primary_key=True)

    status: Mapped[NodeStatus] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(nullable=False)

    __mapper_args__ = {"polymorphic_identity": NodeType.message}


class ConditionNodeConfiguration(BaseNodeConfiguration):
    __tablename__ = "condition_node_configurations"

    id = Column(UUID(as_uuid=True), ForeignKey("node_configurations.id"), primary_key=True)

    condition: Mapped[str] = mapped_column(nullable=False)

    __mapper_args__ = {"polymorphic_identity": NodeType.condition}


class EndNodeConfiguration(BaseNodeConfiguration):
    __tablename__ = "end_node_configurations"

    id = Column(UUID(as_uuid=True), ForeignKey("node_configurations.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": NodeType.end}


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
