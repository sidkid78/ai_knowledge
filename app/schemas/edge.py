"""
Edge schemas for request/response validation.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class EdgeBase(BaseModel):
    """Base edge schema"""
    from_node_id: UUID = Field(..., description="Source node ID")
    to_node_id: UUID = Field(..., description="Target node ID")
    relation_type: str = Field(..., min_length=1, max_length=50, description="Type of relationship")
    axis_values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Axis values for this edge"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this relationship")

class EdgeCreate(EdgeBase):
    """Schema for edge creation"""
    pass

class EdgeUpdate(BaseModel):
    """Schema for edge updates"""
    from_node_id: Optional[UUID] = None
    to_node_id: Optional[UUID] = None
    relation_type: Optional[str] = Field(None, min_length=1, max_length=50)
    axis_values: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class EdgeResponse(EdgeBase):
    """Schema for edge responses"""
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class EdgeFilter(BaseModel):
    """Schema for edge filtering"""
    from_node_id: Optional[UUID] = None
    to_node_id: Optional[UUID] = None
    relation_type: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class EdgeList(BaseModel):
    """Schema for paginated edge lists"""
    items: List[EdgeResponse]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "from_node_id": "456e7890-e89b-12d3-a456-426614174001",
                        "to_node_id": "789e0123-e89b-12d3-a456-426614174002",
                        "relation_type": "influences",
                        "axis_values": {
                            "strength": 0.8,
                            "directional": True
                        },
                        "confidence": 0.9,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        } 