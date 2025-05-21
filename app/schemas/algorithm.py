"""
Schema definitions for algorithm-related data structures.
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

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