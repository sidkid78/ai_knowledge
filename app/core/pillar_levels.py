"""
Pillar Levels system for the UKG.
Defines the 87 hierarchical pillar levels that structure knowledge domains.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class DomainType(Enum):
    """Types of knowledge domains"""
    STEM = "STEM"
    HUMANITIES = "Humanities"
    SOCIAL_SCIENCES = "Social Sciences"
    APPLIED_SCIENCES = "Applied Sciences"
    INTERDISCIPLINARY = "Interdisciplinary"
    PROFESSIONAL = "Professional"
    EMERGING = "Emerging"

@dataclass
class PillarLevelMetadata:
    """Metadata for a pillar level"""
    id: str
    name: str
    description: str
    domain_type: DomainType
    parent_id: Optional[str]
    children_ids: List[str]
    depth: int
    schema_extensions: Dict

# Define the 87 pillar levels hierarchically
PILLAR_LEVELS: Dict[str, PillarLevelMetadata] = {
    # Root Domains (PL01-PL10)
    "PL01": PillarLevelMetadata(
        id="PL01",
        name="Mathematics",
        description="Mathematical concepts and theories",
        domain_type=DomainType.STEM,
        parent_id=None,
        children_ids=["PL11", "PL12", "PL13"],
        depth=0,
        schema_extensions={
            "notation_systems": ["LaTeX", "MathML"],
            "proof_requirements": True
        }
    ),
    "PL02": PillarLevelMetadata(
        id="PL02",
        name="Computer Science",
        description="Computing theory and practice",
        domain_type=DomainType.STEM,
        parent_id=None,
        children_ids=["PL14", "PL15", "PL16"],
        depth=0,
        schema_extensions={
            "programming_paradigms": True,
            "computational_complexity": True
        }
    ),
    # Add more root domains...

    # Level 1 Sub-domains (PL11-PL30)
    "PL11": PillarLevelMetadata(
        id="PL11",
        name="Algebra",
        description="Study of mathematical structures",
        domain_type=DomainType.STEM,
        parent_id="PL01",
        children_ids=["PL31", "PL32"],
        depth=1,
        schema_extensions={}
    ),
    # Add more level 1 domains...

    # Level 2 Sub-domains (PL31-PL50)
    "PL31": PillarLevelMetadata(
        id="PL31",
        name="Group Theory",
        description="Study of algebraic structures called groups",
        domain_type=DomainType.STEM,
        parent_id="PL11",
        children_ids=["PL51", "PL52"],
        depth=2,
        schema_extensions={
            "requires_abstract_algebra": True
        }
    ),
    # Add more level 2 domains...
}

def get_pillar_metadata(pillar_id: str) -> PillarLevelMetadata:
    """Get metadata for a pillar level"""
    return PILLAR_LEVELS[pillar_id]

def get_children(pillar_id: str) -> List[PillarLevelMetadata]:
    """Get children of a pillar level"""
    metadata = get_pillar_metadata(pillar_id)
    return [PILLAR_LEVELS[child_id] for child_id in metadata.children_ids]

def get_parent(pillar_id: str) -> Optional[PillarLevelMetadata]:
    """Get parent of a pillar level"""
    metadata = get_pillar_metadata(pillar_id)
    return PILLAR_LEVELS[metadata.parent_id] if metadata.parent_id else None

def get_ancestors(pillar_id: str) -> List[PillarLevelMetadata]:
    """Get all ancestors of a pillar level"""
    ancestors = []
    current = get_parent(pillar_id)
    while current:
        ancestors.append(current)
        current = get_parent(current.id)
    return ancestors

def get_descendants(pillar_id: str) -> List[PillarLevelMetadata]:
    """Get all descendants of a pillar level"""
    descendants = []
    to_process = [pillar_id]
    
    while to_process:
        current_id = to_process.pop()
        children = get_children(current_id)
        descendants.extend(children)
        to_process.extend(child.id for child in children)
    
    return descendants

def get_siblings(pillar_id: str) -> List[PillarLevelMetadata]:
    """Get siblings of a pillar level"""
    metadata = get_pillar_metadata(pillar_id)
    if not metadata.parent_id:
        return []
    
    parent = get_parent(pillar_id)
    return [PILLAR_LEVELS[child_id] for child_id in parent.children_ids if child_id != pillar_id]

def validate_hierarchy() -> bool:
    """Validate the pillar level hierarchy"""
    for pillar_id, metadata in PILLAR_LEVELS.items():
        # Check parent-child consistency
        if metadata.parent_id:
            parent = PILLAR_LEVELS[metadata.parent_id]
            if pillar_id not in parent.children_ids:
                raise ValueError(f"Parent {parent.id} does not list {pillar_id} as child")
        
        # Check children exist
        for child_id in metadata.children_ids:
            if child_id not in PILLAR_LEVELS:
                raise ValueError(f"Child {child_id} of {pillar_id} does not exist")
            
            child = PILLAR_LEVELS[child_id]
            if child.parent_id != pillar_id:
                raise ValueError(f"Child {child_id} does not reference {pillar_id} as parent")
        
        # Check depth is consistent
        if metadata.parent_id:
            parent = PILLAR_LEVELS[metadata.parent_id]
            if metadata.depth != parent.depth + 1:
                raise ValueError(f"Depth inconsistency for {pillar_id}")
    
    return True 