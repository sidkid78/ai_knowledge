"""
Initialize models package, import Base, and then import all models.
Ensures Base is defined before models use it and helps SQLAlchemy find models.
"""

# Import Base first
from app.db.models_base import Base

# Then import all models that inherit from Base
from .knowledge_node import KnowledgeNode
from .knowledge_edge import KnowledgeEdge
from .pillar_level import PillarLevel
from .algorithm import Algorithm
from .persona import PersonaAgent
from .validation_result import ValidationResult
from .user import User

"""
Initialize models package and import Base.
"""

"""Database models""" 