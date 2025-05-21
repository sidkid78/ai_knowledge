from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from uuid import UUID

class EdgeBase(BaseModel):
    """Base schema for knowledge edges"""
    from_node_id: UUID
    to_node_id: UUID
    relation_type: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    axis_values: Dict[str, Any] = Field(default_factory=dict)

class EdgeCreate(EdgeBase):
    """Schema for creating an edge"""
    pass

class EdgeRead(EdgeBase):
    """Schema for reading an edge"""
    id: UUID

    class Config:
        from_attributes = True

class EdgeUpdate(BaseModel):
    """Schema for updating an edge"""
    relation_type: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    axis_values: Optional[Dict[str, Any]] = None

class EdgeList(BaseModel):
    """Schema for listing edges"""
    edges: List[EdgeRead] 