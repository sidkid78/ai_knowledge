"""
Pillar level SQLAlchemy model.
"""
from sqlalchemy import Column, String, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import VARCHAR
from typing import List, Optional

from app.db.models_base import Base

# Association table for related pillars (for cross-referencing)
pillar_relations = Table('pillar_relations', Base.metadata,
    Column('from_pillar_id', String(5), ForeignKey('pillar_levels.id'), primary_key=True),
    Column('to_pillar_id', String(5), ForeignKey('pillar_levels.id'), primary_key=True)
)

class PillarLevel(Base):
    """
    Represents a hierarchical knowledge domain pillar (PL01-PL87).
    Each pillar represents a specific domain of knowledge or concept space.
    """
    __tablename__ = "pillar_levels"

    # Core fields
    id = Column(String(5), primary_key=True)  # E.g. 'PL01'
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    domain_type = Column(String(50), nullable=False)  # e.g., 'Mathematics', 'Computer Science'
    
    # Hierarchy
    parent_id = Column(String(5), ForeignKey('pillar_levels.id'), nullable=True)
    children = relationship(
        "PillarLevel",
        backref=backref('parent', remote_side=[id]),
        cascade="all, delete"
    )
    
    # Domain-specific schema extensions
    schema_extensions = Column(JSON, default={})  # Custom fields per domain
    
    # Cross-references to related pillars
    related_pillars = relationship(
        'PillarLevel',
        secondary=pillar_relations,
        primaryjoin=id==pillar_relations.c.from_pillar_id,
        secondaryjoin=id==pillar_relations.c.to_pillar_id,
        backref="referenced_by"
    )
    
    # Relationships
    nodes = relationship("KnowledgeNode", back_populates="pillar_level")
    
    def __repr__(self):
        return f"<PillarLevel(id={self.id}, name={self.name}, domain={self.domain_type})>"

    @property
    def full_hierarchy_path(self) -> List[str]:
        """Returns the full path from root to this pillar"""
        path = []
        current = self
        while current:
            path.append(current.id)
            current = current.parent
        return list(reversed(path))

    @property
    def depth(self) -> int:
        """Returns the depth of this pillar in the hierarchy"""
        return len(self.full_hierarchy_path) - 1

    def is_ancestor_of(self, other_pillar: 'PillarLevel') -> bool:
        """Check if this pillar is an ancestor of another pillar"""
        return self.id in other_pillar.full_hierarchy_path[:-1]

    def get_all_descendants(self) -> List['PillarLevel']:
        """Returns all descendants of this pillar"""
        result = []
        for child in self.children:
            result.append(child)
            result.extend(child.get_all_descendants())
        return result