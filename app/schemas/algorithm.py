"""
Schema definitions for algorithm-related data structures.
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class ReasoningStep(BaseModel):
    """
    Represents a single step in an algorithm's reasoning process.
    """
    step_number: int
    description: str
    axis_used: str
    computation: str
    intermediate_value: float

class AlgorithmResult(BaseModel):
    """
    Represents the result of an algorithm execution.
    """
    algorithm_id: str
    input_hash: str
    status: str
    result_value: Optional[float]
    confidence_score: float
    reasoning_trace: List[ReasoningStep]
    execution_time_ms: float
    warnings: List[str]

class AlgorithmMetadata(BaseModel):
    """
    Metadata about an algorithm's capabilities and requirements.
    """
    id: str
    name: str
    description: str
    version: str
    axis_parameters: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class AlgorithmInput(BaseModel):
    """Standard input format for algorithm execution"""
    query: Dict[str, Any] = Field(..., description="Query parameters for the algorithm")
    axis_values: Dict[str, Any] = Field(..., description="Values for each axis being used")
    weights: Optional[Dict[str, float]] = Field(default_factory=dict, description="Optional weights for axes")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional algorithm-specific parameters")

class AlgorithmRead(BaseModel):
    """Schema for reading algorithm metadata"""
    metadata: AlgorithmMetadata
    example_input: Optional[Dict[str, Any]]
    example_output: Optional[Dict[str, Any]]

class AlgorithmInfo(BaseModel):
    """Schema for algorithm information"""
    id: str = Field(..., description="Unique algorithm identifier")
    name: str = Field(..., description="Human-readable algorithm name")
    description: str = Field(..., description="Algorithm description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Algorithm parameters")
    required_axes: List[str] = Field(default_factory=list, description="Required axis names")
    output_type: str = Field(default="any", description="Expected output type")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "ai_knowledge_discovery",
                "name": "AI Knowledge Discovery",
                "description": "Discover hidden patterns and connections using AI",
                "parameters": {
                    "max_depth": {"type": "int", "default": 3, "description": "Maximum search depth"},
                    "confidence_threshold": {"type": "float", "default": 0.7, "description": "Minimum confidence"}
                },
                "required_axes": ["complexity", "novelty"],
                "output_type": "structured"
            }
        }

class AlgorithmList(BaseModel):
    """Schema for algorithm list responses"""
    items: List[AlgorithmInfo]
    total: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "ai_knowledge_discovery",
                        "name": "AI Knowledge Discovery",
                        "description": "Discover hidden patterns and connections using AI",
                        "parameters": {},
                        "required_axes": ["complexity", "novelty"],
                        "output_type": "structured"
                    }
                ],
                "total": 1
            }
        }

class AlgorithmExecuteRequest(BaseModel):
    """Schema for algorithm execution requests"""
    node_id: UUID = Field(..., description="Target node ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Algorithm parameters")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    class Config:
        schema_extra = {
            "example": {
                "node_id": "123e4567-e89b-12d3-a456-426614174000",
                "parameters": {
                    "max_depth": 3,
                    "confidence_threshold": 0.8
                },
                "context": {
                    "user_id": "user123",
                    "session_id": "session456"
                }
            }
        }

class AlgorithmExecuteResponse(BaseModel):
    """Schema for algorithm execution responses"""
    node_id: str = Field(..., description="Node ID that was processed")
    algorithm_id: str = Field(..., description="Algorithm that was executed")
    result: Any = Field(..., description="Algorithm result")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    executed_at: Optional[datetime] = Field(default_factory=datetime.now, description="Execution timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "node_id": "123e4567-e89b-12d3-a456-426614174000",
                "algorithm_id": "ai_knowledge_discovery",
                "result": {
                    "patterns_found": 5,
                    "connections": ["node1", "node2"],
                    "insights": ["Pattern A shows strong correlation"]
                },
                "confidence": 0.87,
                "metadata": {
                    "execution_time_ms": 1250,
                    "memory_used_mb": 45
                },
                "executed_at": "2024-01-01T12:00:00Z"
            }
        }

class BatchExecuteRequest(BaseModel):
    """Schema for batch algorithm execution requests"""
    node_ids: List[UUID] = Field(..., min_items=1, description="List of node IDs to process")
    algorithm_ids: List[str] = Field(..., min_items=1, description="List of algorithms to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Common parameters for all executions")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    priority: int = Field(default=1, ge=1, le=5, description="Task priority (1-5)")
    
    class Config:
        schema_extra = {
            "example": {
                "node_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "456e7890-e89b-12d3-a456-426614174001"
                ],
                "algorithm_ids": ["ai_knowledge_discovery", "pattern_recognition"],
                "parameters": {
                    "max_depth": 3,
                    "confidence_threshold": 0.8
                },
                "priority": 2
            }
        }

class TaskResponse(BaseModel):
    """Schema for task status responses"""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    result: Optional[Any] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: Optional[datetime] = Field(None, description="Task creation time")
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "987fcdeb-51a2-4bc3-9876-543210fedcba",
                "status": "completed",
                "progress": 1.0,
                "message": "Batch execution completed successfully",
                "result": {
                    "total_processed": 2,
                    "successful": 2,
                    "failed": 0,
                    "results": []
                },
                "created_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:05:30Z"
            }
        } 