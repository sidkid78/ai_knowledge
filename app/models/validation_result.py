"""
Validation result SQLAlchemy model.
"""
from sqlalchemy import Column, Float, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.models_base import Base

class ValidationResult(Base):
    """
    Stores validation results for knowledge nodes.
    Tracks confidence scores and validation suggestions.
    """
    __tablename__ = "validation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("persona_agents.id"), nullable=False)
    confidence = Column(Float, nullable=False)
    validation_type = Column(JSON, nullable=False)  # e.g., {"kb": true, "statistical": true}
    suggestions = Column(JSON, nullable=False, default=list)
    sources = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    node = relationship("KnowledgeNode", back_populates="validation_results")
    agent = relationship("PersonaAgent", back_populates="validation_results")

    def __repr__(self):
        return f"<ValidationResult(node_id={self.node_id}, confidence={self.confidence})>"

    def to_dict(self):
        """Convert validation result to dictionary"""
        return {
            "id": str(self.id),
            "node_id": str(self.node_id),
            "agent_id": str(self.agent_id),
            "confidence": self.confidence,
            "validation_type": self.validation_type,
            "suggestions": self.suggestions,
            "sources": self.sources,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 