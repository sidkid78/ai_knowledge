"""
Persona agent SQLAlchemy model.
"""
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

from app.db.models_base import Base

class AgentState(str, Enum):
    """Agent state enumeration"""
    IDLE = "idle"
    PROCESSING = "processing"
    VALIDATING = "validating"
    RESEARCHING = "researching"
    ERROR = "error"

class PersonaAgent(Base):
    """
    Persona agent model representing an AI subsystem with specialized expertise.
    Each agent has domain coverage, available algorithms, and maintains a learning trace.
    """
    __tablename__ = "persona_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    domain_coverage = Column(ARRAY(String), nullable=False)  # List of pillar IDs
    algorithms_available = Column(ARRAY(String), nullable=False)
    state = Column(SQLEnum(AgentState), default=AgentState.IDLE, nullable=False)
    confidence_threshold = Column(JSON, nullable=False, default=lambda: {
        "knowledge_discovery": 0.7,
        "risk_assessment": 0.8,
        "compliance": 0.9
    })
    validation_rules = Column(JSON, nullable=False, default=dict)
    learning_trace = Column(JSON, nullable=False, default=list)
    research_sources = Column(JSON, nullable=False, default=lambda: {
        "internal": ["knowledge_base", "historical_data"],
        "external": ["api_endpoints", "documentation"]
    })
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    validation_results = relationship("ValidationResult", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PersonaAgent(id={self.id}, name='{self.name}', state={self.state.value})>"

    def to_dict(self):
        """Convert agent to dictionary representation"""
        return {
            "id": str(self.id),
            "name": self.name,
            "domain_coverage": self.domain_coverage,
            "algorithms_available": self.algorithms_available,
            "state": self.state.value,
            "confidence_threshold": self.confidence_threshold,
            "validation_rules": self.validation_rules,
            "learning_trace": self.learning_trace,
            "research_sources": self.research_sources,
            "validation_results": [vr.to_dict() for vr in self.validation_results]
        }