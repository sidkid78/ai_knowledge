"""
Node schemas for request/response validation.
"""
from typing import Dict, Any, Optional, List, Annotated
from pydantic import BaseModel, Field, conint
from datetime import datetime
from uuid import UUID
from enum import Enum

class NodeBase(BaseModel):
    """Base node schema"""
    label: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    pillar_level_id: str = Field(..., pattern="^PL[0-9]{2}$")
    axis_values: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Axis values for this node"
    )

class NodeCreate(NodeBase):
    """Schema for node creation"""
    pass

class NodeUpdate(BaseModel):
    """Schema for node updates"""
    label: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    pillar_level_id: Optional[str] = Field(None, pattern="^PL[0-9]{2}$")
    axis_values: Optional[Dict[str, Dict[str, Any]]] = None

class NodeResponse(NodeBase):
    """Schema for node responses"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NodeFilter(BaseModel):
    """Schema for node filtering"""
    pillar_level_id: Optional[str] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    has_validation: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class NodeList(BaseModel):
    """Schema for paginated node lists"""
    items: List[NodeResponse]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "label": "Quantum Computing Fundamentals",
                        "description": "Basic concepts of quantum computing",
                        "pillar_level_id": "PL01",
                        "axis_values": {
                            "complexity": {"value": 0.8, "confidence": 0.9},
                            "novelty": {"value": 0.7, "confidence": 0.8}
                        },
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }

class ProcessNodeRequest(BaseModel):
    """Schema for node processing requests"""
    algorithm_id: str = Field(
        ...,
        description="ID of the algorithm to apply"
    )
    agent_names: Optional[List[str]] = Field(
        None,
        description="Optional list of specific agents to use"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for processing"
    )

class ProcessingResult(BaseModel):
    """Schema for individual agent processing results"""
    agent_name: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class ProcessNodeResponse(BaseModel):
    """Schema for node processing responses"""
    node_id: str
    algorithm_id: str
    results: List[ProcessingResult]

    class Config:
        schema_extra = {
            "example": {
                "node_id": "123e4567-e89b-12d3-a456-426614174000",
                "algorithm_id": "ai_knowledge_discovery",
                "results": [
                    {
                        "agent_name": "Quantum Expert",
                        "success": True,
                        "result": {
                            "confidence": 0.85,
                            "actions": ["Applied algorithm", "Validated results"],
                            "subcalls": []
                        },
                        "error": None,
                        "timestamp": "2024-01-01T12:00:00Z"
                    }
                ]
            }
        }

class ValidationType(str, Enum):
    """Types of validation"""
    KNOWLEDGE_BASE = "knowledge_base"
    STATISTICAL = "statistical"
    PATTERN = "pattern"
    CROSS_REFERENCE = "cross_reference"
    HYBRID = "hybrid"

class BackgroundProcessRequest(BaseModel):
    """Schema for background processing requests"""
    algorithm_id: str = Field(
        ...,
        description="ID of the algorithm to apply"
    )
    # Research options
    perform_research: bool = Field(
        default=False,
        description="Whether to perform autonomous research"
    )
    research_depth: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Depth of research (1-5)"
    )
    
    # Validation options
    perform_validation: bool = Field(
        default=False,
        description="Whether to perform validation"
    )
    validation_type: ValidationType = Field(
        default=ValidationType.HYBRID,
        description="Type of validation to perform"
    )
    
    # Ensemble options
    perform_ensemble: bool = Field(
        default=False,
        description="Whether to perform ensemble reasoning"
    )
    ensemble_size: int = Field(
        default=3,
        ge=2,
        le=10,
        description="Number of agents in ensemble (2-10)"
    )
    
    # General options
    priority: Annotated[int, Field(default=1, ge=1, le=5, description="Task priority (1-5, higher is more important)")]
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for processing"
    )

    class Config:
        schema_extra = {
            "example": {
                "algorithm_id": "ai_knowledge_discovery",
                "perform_research": True,
                "research_depth": 2,
                "perform_validation": True,
                "validation_type": "hybrid",
                "perform_ensemble": True,
                "ensemble_size": 3,
                "priority": 2,
                "parameters": {
                    "confidence_threshold": 0.8,
                    "max_suggestions": 5
                }
            }
        }

class TaskStatus(str, Enum):
    """Background task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskResponse(BaseModel):
    """Schema for task responses"""
    node_id: str
    task_ids: List[str]
    status: Optional[TaskStatus] = None
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "node_id": "123e4567-e89b-12d3-a456-426614174000",
                "task_ids": ["987fcdeb-51a2-4bc3-9876-543210fedcba"],
                "status": "completed",
                "message": "Task completed successfully",
                "result": {
                    "findings": [
                        {
                            "type": "new_connection",
                            "confidence": 0.85,
                            "details": "Found related concept in quantum algorithms"
                        }
                    ],
                    "metrics": {
                        "processing_time": 2.5,
                        "confidence_score": 0.9
                    }
                },
                "started_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:00:05Z"
            }
        } 