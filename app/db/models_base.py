"""
Base model and metadata for SQLAlchemy.
"""
from sqlalchemy.orm import declarative_base

# Centralized Base for all models
Base = declarative_base()

# Models are imported in app/models/__init__.py 