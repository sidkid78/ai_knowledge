from sqlalchemy import Column, String, ForeignKey 
from sqlalchemy.orm import relationship 
from sqlalchemy.dialects.postgresql import VARCHAR 
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PillarLevel(Base):
    __tablename__ = "pillar_levels"

    id = Column(String(5), primary_key=True) # E.g. 'PL01'
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    parent_id = Column(String(5), ForeignKey('pillar_levels.id'), nullable=True)