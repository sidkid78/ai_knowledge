"""
Utilities for extending and managing pillar levels.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.pillar_level import PillarLevel
from app.core.pillar_levels import (
    DomainType,
    PillarLevelMetadata,
    validate_hierarchy,
    PILLAR_LEVELS
)

def add_pillar_level(
    db: Session,
    id: str,
    name: str,
    description: str,
    domain_type: DomainType,
    parent_id: Optional[str] = None,
    schema_extensions: Optional[Dict[str, Any]] = None
) -> PillarLevel:
    """
    Add a new pillar level to the system.
    
    Args:
        db: Database session
        id: Pillar level ID (e.g., 'PL88')
        name: Name of the pillar level
        description: Description of the domain
        domain_type: Type of domain (from DomainType enum)
        parent_id: Optional parent pillar level ID
        schema_extensions: Optional schema extensions
    """
    # Validate ID format
    if not id.startswith('PL') or not id[2:].isdigit():
        raise ValueError("Pillar ID must be in format 'PLxx' where xx is a number")
    
    # Check if ID already exists
    if db.query(PillarLevel).filter(PillarLevel.id == id).first():
        raise ValueError(f"Pillar level {id} already exists")
    
    # Validate parent exists if specified
    parent = None
    if parent_id:
        parent = db.query(PillarLevel).filter(PillarLevel.id == parent_id).first()
        if not parent:
            raise ValueError(f"Parent pillar level {parent_id} not found")
    
    # Calculate depth
    depth = parent.depth + 1 if parent else 0
    
    # Create new pillar level
    pillar = PillarLevel(
        id=id,
        name=name,
        description=description,
        domain_type=domain_type.value,
        parent_id=parent_id,
        depth=depth,
        schema_extensions=schema_extensions or {}
    )
    
    # Update parent's children list if needed
    if parent:
        if not parent.children_ids:
            parent.children_ids = []
        parent.children_ids.append(id)
        db.add(parent)
    
    db.add(pillar)
    db.commit()
    
    # Update in-memory registry
    PILLAR_LEVELS[id] = PillarLevelMetadata(
        id=id,
        name=name,
        description=description,
        domain_type=domain_type,
        parent_id=parent_id,
        children_ids=[],
        depth=depth,
        schema_extensions=schema_extensions or {}
    )
    
    # Validate hierarchy remains consistent
    validate_hierarchy()
    
    return pillar

def bulk_add_pillar_levels(
    db: Session,
    pillar_data: List[Dict[str, Any]]
) -> List[PillarLevel]:
    """
    Add multiple pillar levels in bulk.
    
    Args:
        db: Database session
        pillar_data: List of dictionaries containing pillar level data
    """
    results = []
    
    # Sort by depth to ensure parents are created first
    sorted_data = sorted(pillar_data, 
                        key=lambda x: len(x.get('parent_id', '').split('.')))
    
    for data in sorted_data:
        pillar = add_pillar_level(
            db=db,
            id=data['id'],
            name=data['name'],
            description=data['description'],
            domain_type=DomainType[data['domain_type']],
            parent_id=data.get('parent_id'),
            schema_extensions=data.get('schema_extensions')
        )
        results.append(pillar)
    
    return results

def get_domain_structure(db: Session, root_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get hierarchical structure of domains.
    
    Args:
        db: Database session
        root_id: Optional root pillar level ID to start from
    """
    def build_tree(pillar_id: str) -> Dict[str, Any]:
        pillar = db.query(PillarLevel).filter(PillarLevel.id == pillar_id).first()
        if not pillar:
            return None
            
        children = []
        if pillar.children_ids:
            for child_id in pillar.children_ids:
                child_tree = build_tree(child_id)
                if child_tree:
                    children.append(child_tree)
        
        return {
            "id": pillar.id,
            "name": pillar.name,
            "description": pillar.description,
            "domain_type": pillar.domain_type,
            "depth": pillar.depth,
            "children": children
        }
    
    if root_id:
        return build_tree(root_id)
    
    # Get all root domains
    roots = db.query(PillarLevel).filter(PillarLevel.parent_id.is_(None)).all()
    return {
        "domains": [build_tree(root.id) for root in roots]
    }

def suggest_pillar_placement(
    db: Session,
    name: str,
    description: str,
    domain_type: DomainType
) -> List[Dict[str, Any]]:
    """
    Suggest potential parent domains for a new pillar level.
    
    Args:
        db: Database session
        name: Proposed name
        description: Proposed description
        domain_type: Proposed domain type
    """
    suggestions = []
    
    # Find domains of the same type
    same_type_domains = (
        db.query(PillarLevel)
        .filter(PillarLevel.domain_type == domain_type.value)
        .all()
    )
    
    for domain in same_type_domains:
        # Calculate simple text similarity
        name_overlap = len(set(name.lower().split()) & 
                         set(domain.name.lower().split()))
        desc_overlap = len(set(description.lower().split()) & 
                         set(domain.description.lower().split()))
        
        similarity = (name_overlap + desc_overlap) / (
            len(name.split()) + len(description.split())
        )
        
        if similarity > 0.2:  # Arbitrary threshold
            suggestions.append({
                "parent_id": domain.id,
                "parent_name": domain.name,
                "similarity_score": similarity,
                "reasoning": f"Similar terminology in name and description, "
                           f"same domain type ({domain_type.value})"
            })
    
    return sorted(suggestions, key=lambda x: x["similarity_score"], reverse=True) 