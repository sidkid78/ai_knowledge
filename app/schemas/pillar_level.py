from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PillarLevelBase(BaseModel):
    """Base Pydantic model for Pillar Levels"""
    name: str
    description: Optional[str] = None
    domain_type: str
    schema_extensions: Dict[str, Any] = Field(default_factory=dict)

class PillarLevelCreate(PillarLevelBase):
    """Schema for creating a new Pillar Level"""
    id: str = Field(..., pattern="^PL[0-9]{2}$", description="Pillar level ID (PL01-PL87)")
    parent_id: Optional[str] = Field(None, pattern="^PL[0-9]{2}$")
    
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

class PillarLevelResponse(PillarLevelBase):
    """Schema for pillar level API responses"""
    id: str
    parent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class PillarLevelUpdate(BaseModel):
    """Schema for updating a Pillar Level"""
    name: Optional[str] = None
    description: Optional[str] = None
    domain_type: Optional[str] = None
    parent_id: Optional[str] = Field(None, pattern="^PL[0-9]{2}$")
    schema_extensions: Optional[Dict[str, Any]] = None

class PillarLevelFilter(BaseModel):
    """Schema for filtering pillar levels"""
    parent_id: Optional[str] = Field(None, pattern="^PL[0-9]{2}$")
    domain_type: Optional[str] = None
    name_contains: Optional[str] = None
    has_children: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class PillarLevelRelation(BaseModel):
    """Schema for creating pillar relationships"""
    from_pillar_id: str = Field(..., pattern="^PL[0-9]{2}$")
    to_pillar_id: str = Field(..., pattern="^PL[0-9]{2}$")
    
class PillarLevelHierarchy(BaseModel):
    """Schema for representing the complete pillar hierarchy"""
    id: str
    name: str
    children: List['PillarLevelHierarchy'] = []
    
    class Config:
        orm_mode = True

class PillarLevelList(BaseModel):
    """Schema for paginated pillar level lists"""
    items: List[PillarLevelResponse]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "PL01",
                        "name": "Quantum Computing",
                        "description": "Fundamental quantum computing concepts",
                        "domain_type": "technical",
                        "parent_id": None,
                        "schema_extensions": {},
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }

# Needed for recursive Pydantic models
PillarLevelRead.update_forward_refs()
PillarLevelHierarchy.update_forward_refs()
        
