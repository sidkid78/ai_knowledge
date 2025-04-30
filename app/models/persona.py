from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid, datetime
from pillar_level import Base

class PersonaAgent(Base):
    __tablename__ = "persona_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    domain_coverage = Column(JSON, default=[])        # List of PillarLevel IDs
    algorithms_available = Column(JSON, default=[])   # List of Algorithm IDs
    running_state = Column(String(20), default="idle")
    learning_trace = Column(JSON, default=[])         # History/events
    created_at = Column(DateTime, default=datetime.datetime.utcnow)