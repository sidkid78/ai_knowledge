from pydantic import BaseModel, Field
from uuid import UUID 
from typing import Optional, Dict, Any 

class NodeCreate(BaseModel):
    label: str 
    description: Optional[str]
    pillar_level_id: str 
    axis_values: Dict[str, Any] = Field(default_factory=dict)

class NodeRead(NodeCreate):
    id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]
