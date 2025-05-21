"""
Knowledge node SQLAlchemy model.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.models_base import Base
from app.models.pillar_level import PillarLevel

class KnowledgeNode(Base):
    """
    Knowledge node model representing a vertex in the knowledge graph.
    Each node has a set of axis values and belongs to a pillar level.
    """
    __tablename__ = "knowledge_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String(200), nullable=False, index=True)
    description = Column(String(2000))
    pillar_level_id = Column(String(4), ForeignKey("pillar_levels.id"), nullable=False)
    axis_values = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    pillar_level = relationship("PillarLevel", back_populates="nodes")
    outgoing_edges = relationship(
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.from_node_id",
        back_populates="from_node"
    )
    incoming_edges = relationship(
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.to_node_id",
        back_populates="to_node"
    )
    validation_results = relationship("ValidationResult", back_populates="node", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<KnowledgeNode(id={self.id}, label='{self.label}')>"
        
    def to_dict(self):
        """Convert node to dictionary"""
        return {
            "id": str(self.id),
            "label": self.label,
            "description": self.description,
            "pillar_level_id": self.pillar_level_id,
            "axis_values": self.axis_values,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "validation_results": [vr.to_dict() for vr in self.validation_results]
        }