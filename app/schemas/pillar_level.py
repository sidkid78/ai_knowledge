from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PillarLevelBase(BaseModel):
    """Base Pydantic model for Pillar Levels"""
    name: str
    description: Optional[str] = None
    domain_type: str
    schema_extensions: Dict[str, Any] = Field(default_factory=dict)

class PillarLevelCreate(PillarLevelBase):
    """Schema for creating a new Pillar Level"""
    id: str  # PL01-PL87
    parent_id: Optional[str] = None
    
class PillarLevelRead(PillarLevelBase):
    """Schema for reading a Pillar Level"""
    id: str
    parent_id: Optional[str] = None
    children: List['PillarLevelRead'] = []
    related_pillars: List[str] = []  # List of related pillar IDs
    depth: int
    full_hierarchy_path: List[str]

    class Config:
        orm_mode = True

class PillarLevelUpdate(BaseModel):
    """Schema for updating a Pillar Level"""
    name: Optional[str] = None
    description: Optional[str] = None
    domain_type: Optional[str] = None
    parent_id: Optional[str] = None
    schema_extensions: Optional[Dict[str, Any]] = None

class PillarLevelRelation(BaseModel):
    """Schema for creating pillar relationships"""
    from_pillar_id: str
    to_pillar_id: str
    
class PillarLevelHierarchy(BaseModel):
    """Schema for representing the complete pillar hierarchy"""
    id: str
    name: str
    children: List['PillarLevelHierarchy'] = []
    
    class Config:
        orm_mode = True

class PillarLevelList(BaseModel):
    """Schema for listing multiple Pillar Levels"""
    pillar_levels: List[PillarLevelRead]

    class Config:
        orm_mode = True

# Needed for recursive Pydantic models
PillarLevelRead.update_forward_refs()
PillarLevelHierarchy.update_forward_refs()
        
