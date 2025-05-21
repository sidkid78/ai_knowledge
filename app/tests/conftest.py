"""
Pytest configuration file for fixtures.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models_base import Base # Import Base with all metadata
from app.core.config import settings

# Use the database URL from settings
# Convert Pydantic DSN object to string for SQLAlchemy
engine = create_engine(str(settings.DATABASE_URL))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Creates all tables before the test session starts and drops them after."""
    print("\nCreating test tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Test tables created.")
        yield # Run tests
    finally:
        print("\nDropping test tables...")
        Base.metadata.drop_all(bind=engine)
        print("Test tables dropped.")

# Modify the existing SessionLocal import in tests to use TestingSessionLocal if needed,
# or ensure DATABASE_URL points to a test-specific DB. 