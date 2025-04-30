import uuid
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from knowledge_node import Base
from sqlalchemy.dialects.postgresql import JSON

class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_node_id = Column(UUID(as_uuid=True), ForeignKey('knowledge_nodes.id'), nullable=False)
    to_node_id = Column(UUID(as_uuid=True), ForeignKey('knowledge_nodes.id'), nullable=False)
    relation_type = Column(String(50), nullable=False)
    axis_values = Column(JSON, default={})
    confidence = Column(Float, default=1.0)

    from_node = relationship("KnowledgeNode", foreign_keys=[from_node_id])
    to_node = relationship("KnowledgeNode", foreign_keys=[to_node_id])