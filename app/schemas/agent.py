"""
Agent schemas for request/response validation.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class AgentBase(BaseModel):
    """Base agent schema"""
    name: str = Field(..., min_length=1, max_length=100)
    domain_coverage: List[str] = Field(..., min_items=1)
    algorithms_available: List[str] = Field(..., min_items=1)

class AgentCreate(AgentBase):
    """Schema for agent creation"""
    pass

class AgentUpdate(BaseModel):
    """Schema for agent updates"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    domain_coverage: Optional[List[str]] = None
    algorithms_available: Optional[List[str]] = None

class AgentResponse(AgentBase):
    """Schema for agent responses"""
    id: UUID
    learning_trace: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ProcessRequest(BaseModel):
    """Schema for node processing requests"""
    node_id: str
    algorithm_id: str
    additional_agent_ids: List[str] = Field(default_factory=list)
    max_recursion: int = Field(default=3, ge=1, le=10)
    parameters: Dict[str, Any] = Field(default_factory=dict) 