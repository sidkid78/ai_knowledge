from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models_base import Base
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.models.pillar_level import PillarLevel
from app.models.persona import PersonaAgent
from app.models.algorithm import Algorithm
from .session import engine
from .seed_data import seed_database

def init_db(seed: bool = True) -> None:
    """
    Initialize the database with all tables
    
    Args:
        seed: Whether to seed the database with initial data
    """
    print(f"Initializing database: {settings.POSTGRES_DB}")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    if seed:
        print("Seeding database with initial data...")
        seed_database()

def drop_db() -> None:
    """Drop all tables - USE WITH CAUTION!"""
    print(f"WARNING: Dropping all tables in {settings.POSTGRES_DB}")
    confirm = input("Are you sure? (type 'yes' to confirm): ")
    if confirm.lower() == 'yes':
        Base.metadata.drop_all(bind=engine)
        print("Database dropped successfully!")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Initialize the database')
    parser.add_argument('--no-seed', action='store_true', help='Skip seeding initial data')
    parser.add_argument('--drop', action='store_true', help='Drop existing tables first')
    args = parser.parse_args()
    
    if args.drop:
        drop_db()
    
    init_db(seed=not args.no_seed) 