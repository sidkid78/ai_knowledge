from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import datetime

class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    pillar_level_id = Column(String(5), ForeignKey('pillar_levels.id'), nullable=False)
    axis_values = Column(JSON, default={})  # e.g., {"pillar_function": ..., "temporal_axis": ...}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    pillar_level = relationship("PillarLevel", back_populates="nodes")