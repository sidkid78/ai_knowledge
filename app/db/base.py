"""
Database configuration and session management.
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.models_base import Base

# Import all models to register them with Base
from app.models.algorithm import Algorithm
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.models.pillar_level import PillarLevel
from app.models.persona import PersonaAgent

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")

